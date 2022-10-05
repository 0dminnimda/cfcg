from subprocess import check_output
from typing import List, Optional
from distutils.ccompiler import new_compiler, CCompiler

import pycparser
from pycparser import c_ast


# def fixed_spawn(self: CCompiler, cmd: List[str]) -> None:
#     if self.dry_run:
#         return "<>"
#     check_output(path_list, input=source, universal_newlines=True)


# def new_fixed_compiler():
#     compiler = new_compiler()
#     compiler.spawn = check_output

def preprocess(source: str, cc: Optional[str] = None) -> str:
    # if cc is None:
    #     compiler = new_compiler(dry_run=1)
    #     compiler.compile(["<test>.c"])
    #     try:
    #         cc = [compiler.cc]
    #     except AttributeError:
    #         cc = compiler.compiler

    # path_list = cc + ["-E"]

    # try:
    #     text = check_output(path_list, input=source, universal_newlines=True)
    # except OSError as e:
    #     raise RuntimeError("Unable to invoke 'cpp'.  " +
    #         'Make sure its path was passed correctly\n' +
    #         ('Original error: %s' % e))

    return source


class CParser(pycparser.CParser):
    def p_pp_directive(self, p):
        pass


def parse(source: str, filename: str = "<unknown>", **kwargs) -> c_ast.Node:
    parser = CParser(**kwargs)
    return parser.parse(preprocess(source), filename)
