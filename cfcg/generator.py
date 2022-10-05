from contextlib import contextmanager
from typing import List, Tuple

from pycparser import c_ast

from parser import parse  # FIXME: use relative import


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

    def put(self, line: str) -> None:
        self.lines.append("    " * self.level + line)

    @contextmanager
    def indent(self):
        try:
            self.level += 1
            yield
        finally:
            self.level -= 1

    def alias(self, text: str) -> str:
        return f'["{text}"]'

    def subgraph_name(self) -> str:
        return f"subgraph SG{self.subgraph_id}"

    def subgraph(self, text: str = " ") -> str:
        return self.subgraph_name() + self.alias(text)

    def node_name(self) -> str:
        return f"n{self.subgraph_id}_{self.node_id}"

    # def node(self, text: str = " ") -> str:
    #     return self.node_name() + self.alias(text)

    def next_node_name(self) -> str:
        self.node_id += 1
        return self.node_name()

    def next_node(self, text: str = " ") -> str:
        return self.next_node_name() + self.alias(text)

    # def visit(self, node):
    #     print(node)
    #     return super().visit(node)

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        self.put(self.subgraph())
        self.subgraph_id += 1

        with self.indent():
            self.put("direction TB")
            self.visit(node.decl)
            self.generic_visit(node.body)  # !!! I may need to visit other fields

            for a, b in self.connections:
                self.put(f"{a} --> {b}")

        self.put("end")

    def visit_FuncDecl(self, node: c_ast.FuncDecl) -> None:
        args = ""
        if node.args:
            args = ", ".join((arg.name for arg in node.args.params))

        text = f"{node.type.declname}({args})"
        self.put(self.next_node(text))


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
