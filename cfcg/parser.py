from distutils.ccompiler import CCompiler, new_compiler
import io
import os
from pathlib import Path
from subprocess import check_output
from typing import List, Optional

import pycparser
from pcpp import Preprocessor
from pycparser import c_ast


def fixed_spawn(self: CCompiler, cmd: List[str]) -> None:
    print(cmd)
    if self.dry_run:
        return
    # check_output(path_list, input=source, universal_newlines=True)


def new_fixed_compiler(*args, **kwargs):
    compiler = new_compiler(*args, **kwargs)
    type(compiler).spawn = fixed_spawn
    return compiler


FAKE_LIBC = "pycparser\\utils\\fake_libc_include"


def preprocess(source: str, filename: str = "<unknown>") -> str:
    # if cc is None:
    #     compiler = new_fixed_compiler(dry_run=1)
    #     compiler.compile(["<test>.c"], include_dirs=["../utils/fake_libc_include"], extra_postargs=["-E"])
    #     try:
    #         cc = [compiler.cc]
    #     except AttributeError:
    #         cc = compiler.compiler
    #     print(cc)

    # exit()

    # path_list = cc + ["-E"]

    # try:
    #     text = check_output(path_list, input=source, universal_newlines=True)
    # except OSError as e:
    #     raise RuntimeError("Unable to invoke 'cpp'.  " +
    #         'Make sure its path was passed correctly\n' +
    #         ('Original error: %s' % e))

    p = Preprocessor()
    p.add_path(Path(__file__).parent.parent / FAKE_LIBC)

    p.parse(source, filename)

    p.write(output := io.StringIO())
    return output.getvalue()

    # # dirty hack to make pycparser work
    # source = "\n".join(
    #     (line for line in source.split("\n") if not line.startswith("#include"))
    # )

    # return source


# class CParser(pycparser.CParser):
#     def p_pp_directive(self, p):
#         pass


def parse(source: str, filename: str = "<unknown>", **kwargs) -> c_ast.Node:
    parser = pycparser.CParser(**kwargs)
    return parser.parse(preprocess(source, filename), filename)
