import ast
from contextlib import contextmanager
from typing import List, Optional, Tuple

from pycparser import c_ast

from parser import parse  # FIXME: use relative import


from enum import Enum


class NodeType(Enum):
    Box = "[", "]"
    RoundedBox = "(", ")"
    Capsule = "([", "])"
    Subroutine = "[[", "]]"
    Circle = "((", "))"
    Rhombus = "{", "}"
    Hexagon = "{{", "}}"
    RightTilted = "[/", "/]"
    LeftTilted = "[\\", "\\]"
    # the rest is not important for us


class ChartGenerator(c_ast.NodeVisitor):
    lines: List[str]
    level: int

    subgraph_id: int
    node_id: int

    connections: List[Tuple[str, str]]

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.lines = ["flowchart TB"]
        self.level = 1

        self.subgraph_id = 0
        self.node_id = 0

        self.connections = []

    def generate(self, node: c_ast.Node) -> str:
        self.reset()
        self.visit(node)
        return "\n".join(self.lines)

    def put(self, line: Optional[str]) -> None:
        if line is not None:
            self.lines.append("    " * self.level + line)

    @contextmanager
    def indent(self):
        try:
            self.level += 1
            yield
        finally:
            self.level -= 1

    def connect(self, a: str, b: str) -> None:
        self.connections.append((a, b))

    def alias(self, text: str, type: NodeType = NodeType.Box) -> str:
        return type.value[0] + repr(text) + type.value[1]

    def subgraph_name(self) -> str:
        return f"subgraph SG{self.subgraph_id}"

    def subgraph(self, text: str = " ", type: NodeType = NodeType.Box) -> str:
        return self.subgraph_name() + self.alias(text, type)

    def node_name(self) -> str:
        return f"n{self.subgraph_id}_{self.node_id}"

    # def node(self, text: str = " ", type: NodeType = NodeType.Box) -> str:
    #     return self.node_name() + self.alias(text, type)

    def next_node_name(self) -> str:
        self.node_id += 1
        return self.node_name()

    def next_node(self, text: str = " ", type: NodeType = NodeType.Box) -> str:
        return self.next_node_name() + self.alias(text, type)

    # def put_next_node(self, node: c_ast.Node) -> bool:
    #     result = self.visit(node)
    #     if result is not None:
    #         assert isinstance(node, str)
    #         self.put(self.next_node(result))
    #         return True
    #     return False

    # def visit(self, node):
    #     print(node)
    #     return super().visit(node)

    def visit_s(self, node: c_ast.Node) -> str:
        result = str(self.visit(node))
        assert isinstance(result, str)
        return result

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        self.put(self.subgraph())
        self.subgraph_id += 1

        with self.indent():
            self.put("direction TB")
            self.visit(node.decl)
            self.visit(node.body)  # !!! I may need to visit other fields

            for a, b in self.connections:
                self.put(f"{a} --> {b}")

        self.put("end")

    def visit_FuncDecl(self, node: c_ast.FuncDecl) -> None:
        args = ""
        if node.args:
            args = ", ".join((arg.name for arg in node.args.params))

        text = f"{node.type.declname}({args})"
        self.put(self.next_node(text))

    def visit_Compound(self, node: c_ast.Compound) -> None:
        for item in node.block_items:
            prev = self.node_name()
            result = self.visit(item)
            if result is not None:
                assert isinstance(item, str)
                self.put(self.next_node(result))
                self.connect(prev, self.node_name())

    def visit_FuncCall(self, node: c_ast.FuncCall) -> Optional[str]:
        if node.name.name == "printf":
            prev = self.node_name()
            self.visit_printf(node)
            self.connect(prev, self.node_name())
            return None
        if node.name.name == "scanf":
            prev = self.node_name()
            self.visit_scanf(node)
            self.connect(prev, self.node_name())
            return None

        args = ""
        if node.args:
            args = ", ".join((self.visit_s(arg) for arg in node.args.exprs))

        return f"{node.name.name}({args})"

    def visit_ID(self, node: c_ast.ID) -> str:
        return node.name

    def visit_printf(self, node: c_ast.FuncCall) -> None:
        assert node.args
        if len(node.args.exprs) == 1:
            text = ast.literal_eval(self.visit(node.args.exprs[0]))
        else:
            text = ", ".join((self.visit_s(arg) for arg in node.args.exprs[1:]))
        self.put(self.next_node("Output: " + text, NodeType.RightTilted))

    def visit_scanf(self, node: c_ast.FuncCall) -> None:
        assert node.args
        text = ", ".join((arg.expr.name for arg in node.args.exprs[1:]))
        self.put(self.next_node("Input: " + text, NodeType.RightTilted))

    def visit_Constant(self, node: c_ast.Constant) -> str:
        return node.value


def generate_chart(code: str, filename: str = "<unknown>") -> str:
    ast = parse(code, filename)
    ast.show()
    return ChartGenerator().generate(ast)


# source = "int main() { float b = 2.7;\nreturn (int)(5 + 7 + b); }"
source = r"""
#include <stdio.h>
#include <math.h>

int maximize(int n) {
    int size = ceil(log10(n));
    int sorted = 0;
    while (sorted != 1) {
        sorted = 1;
        int offset = 1;
        for (int i = 0; i < size - 1; i++) {
            int digit1 = n / (offset*10) % 10;
            int digit2 = n / (offset   ) % 10;
            if (digit1 > digit2) {
                n = n - digit1 * offset * 10 + digit2 * offset * 10;
                n = n - digit2 * offset      + digit1 * offset     ;
                sorted = 0;
            }
            offset *= 10;
        }
    }
    return n;
}

int main() {
    printf("Hello! Input one integer\n");
    int n = 0;
    scanf("%d", &n);
    if (n > 0)
        printf("Minimal digit combination: %d (leading zeros are not shown)\n", maximize(n));
    else
        printf("It's not an integer ;(\nSorry, but you'll have to enter an integer next time!\n");
    return 0;
}
"""
print(generate_chart(source, "c.c"))
