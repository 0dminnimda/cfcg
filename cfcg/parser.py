import io
from pathlib import Path

from pcpp import Preprocessor
from pycparser import CParser, c_ast

FAKE_LIBC = "pycparser\\utils\\fake_libc_include"


def preprocess(source: str, filename: str = "<unknown>") -> str:
    p = Preprocessor()
    p.add_path(Path(__file__).parent.parent / FAKE_LIBC)

    p.parse(source, filename)

    p.write(output := io.StringIO())
    return output.getvalue()


def parse(source: str, filename: str = "<unknown>", **kwargs) -> c_ast.Node:
    parser = CParser(**kwargs)
    return parser.parse(preprocess(source, filename), filename)
