"""Tests for ast_visitor module (pytest)"""
import configparser
import ast
import io
# pylint: disable= invalid-name, missing-docstring, no-self-use, too-few-public-methods

from ast_visitor import TreeVisitor
from puml_generator import PUML_Generator

cfg = configparser.ConfigParser()
cfg.read('py2puml.ini')

class Test_TreeVisitor(object):
    def test_init(self):
        visitor = TreeVisitor(ast.Module())
        assert visitor

    def py2puml(self, sourcefile, config=cfg):
        gen = PUML_Generator(dest=io.StringIO(), config=config)
        gen.header()
        gen.do_file(sourcefile)
        gen.footer()
        return gen.dest.getvalue()

    def test_visit(self):
        puml = self.py2puml('examples/person.py')
        with open('examples/person.puml') as f:
            expected = f.read()
        assert puml == expected

    def test_visit1(self):
        puml = self.py2puml('py2puml.py')
        with open('examples/py2puml.puml') as f:
            expected = f.read()
        assert puml == expected
