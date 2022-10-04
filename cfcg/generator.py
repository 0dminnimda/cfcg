from pycparser import c_ast, CParser


def parse(source: str, filename: str = "<unknown>", **kwargs) -> c_ast.Node:
    parser = CParser(**kwargs)
    return parser.parse(source, filename)


class FuncCallVisitor(c_ast.NodeVisitor):
    def visit(self, node):
        print(node)
        return super().visit(node)


def show_func_calls(code):
    ast = parse(code)
    v = FuncCallVisitor()
    v.visit(ast)


show_func_calls("int main() { return 5 + 7; }")
