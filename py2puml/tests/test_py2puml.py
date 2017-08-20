"""Tests for py2puml (pytest)"""
import configparser
import ast
import io
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring, no-self-use, too-few-public-methods

from py2puml import ClassInfo, TreeVisitor, PUML_Generator, PUML_Generator_NS, run, cli_parser

cfg = configparser.ConfigParser()
cfg.read('py2puml.ini')

@pytest.fixture
def ast_class0():
    """AST tree of an empty class"""
    return ast.parse("class MyClass: pass").body[0]

@pytest.fixture
def ast_class1():
    """AST tree of a simple class"""
    tree = ast.parse("class MyClass:\n"
                     "    i = 12345\n"
                     "\n"
                     "    def f(self):\n"
                     "        return 'hello world'\n")
    return tree.body[0]

class Test_ClassInfo(object):
    @staticmethod
    def test_visibility():
        assert ClassInfo.visibility('__builtin__') == '-'
        assert ClassInfo.visibility('_private') == '-'
        assert ClassInfo.visibility('public') == '+'

    def test_init(self, ast_class1):
        print(ast.dump(ast_class1))
        cdef = ClassInfo(ast_class1)
        assert cdef.classname == "MyClass"

    def test_add_member(self, ast_class0):
        cdef = ClassInfo(ast_class0)
        cdef.add_member('member')
        assert cdef.members == ['member']

class Test_PUML_Generator(object):
    pyfilename = 'some/sub/path/module.py'

    @staticmethod
    @pytest.fixture
    def gen():
        dest = io.StringIO()
        return PUML_Generator(dest, config=cfg)

    def test_init(self, gen):
        assert gen.dest.write

    def test_header(self, gen):
        gen.header()
        assert gen.dest.tell() == 80
        assert gen.dest.getvalue() == """\
@startuml
skinparam monochrome true
skinparam classAttributeIconSize 0
scale 2

"""
    def test_footer(self, gen):
        gen.header()
        gen.start_file(self.pyfilename)
        p = gen.dest.tell()
        gen.footer()
        assert gen.dest.getvalue()[p:] == """\
' customizable epilog
' here you may add notes and associations

@enduml
"""

class Test_PUML_Generator_NS(object):
    pyfilename = 'some/sub/path/module.py'

    @staticmethod
    @pytest.fixture
    def gen():
        dest = io.StringIO()
        return PUML_Generator_NS(dest, root='.', config=cfg)

    def test_init(self, gen):
        assert gen.namespaces == []
        assert gen.depth == 0

    def test_start_file(self, gen):
        gen.start_file(self.pyfilename)
        assert gen.namespaces == ['some', 'sub', 'path', 'module']
        assert gen.depth == 4
        gen.start_file('some/sub/other_module.py')
        assert gen.namespaces == ['some', 'sub', 'other_module']
        assert gen.depth == 3

    def test_header(self, gen):
        # initially no indentation
        assert gen.depth == 0
        gen.header()
        gen.start_file(self.pyfilename)
        # generating header increases indentation
        assert gen.depth == 4
        assert gen.dest.tell() == 161
        assert gen.dest.getvalue() == """\
@startuml
skinparam monochrome true
skinparam classAttributeIconSize 0
scale 2

namespace some {
  namespace sub {
    namespace path {
      namespace module {
"""

    def test_footer(self, gen):
        gen.header()
        gen.start_file(self.pyfilename)
        p = gen.dest.tell()
        gen.footer()
        assert gen.dest.getvalue()[p:] == """\
      }
    }
  }
}
' customizable epilog
' here you may add notes and associations

@enduml
"""
    #TODO test static methods and class variables

class Test_TreeVisitor(object):
    def test_init(self):
        visitor = TreeVisitor(ast.Module())
        assert visitor

    def py2puml(self, sourcefile):
        gen = PUML_Generator(dest=io.StringIO(), config=cfg)
        with open(sourcefile) as f:
            tree = ast.parse(f.read())
        visitor = TreeVisitor(gen)
        gen.header()
        gen.start_file(sourcefile)
        visitor.visit(tree)
        gen.end_file(sourcefile)
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

#TODO test multiple input files
def test_run_multiple_sources(capsys):
    args = cli_parser().parse_args(
        '--root . py2puml.py puml_generator.py'.split())
    assert args.root == '.'
    assert args.py_file == ['py2puml.py', 'puml_generator.py']
    assert args.root == '.'
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    assert out.count('namespace ') == 2
    assert out.count('class ') == 4

    with open('examples/py2puml_NS.puml') as f:
        expected = f.read()
    assert out == expected


# TODO test error cases
