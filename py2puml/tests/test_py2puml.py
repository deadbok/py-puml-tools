"""Tests for py2puml (pytest)"""
import ast
import io
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring, no-self-use, too-few-public-methods

from py2puml import ClassInfo, TreeVisitor, PUML_Generator


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

# pylint  disable=redefined-outer-name #                 W0621
@pytest.fixture
def gen1():
    dest = io.StringIO()
    return PUML_Generator('some/sub/path/module.py', dest=dest)

class Test_PUML_Generator(object):
    def test_init(self, gen1):
        assert gen1.namespaces == ['some', 'sub', 'path', 'module']
        assert gen1.tabs == 0

    def test_depth(self, gen1):
        assert gen1.depth == 4

    def test_header(self, gen1):
        gen1.header()
        assert gen1.tabs == 4
        assert gen1.dest.tell() == 161
        assert gen1.dest.getvalue() == """\
@startuml
skinparam monochrome true
skinparam classAttributeIconSize 0
scale 2

namespace some {
  namespace sub {
    namespace path {
      namespace module {
"""

    def test_footer(self, gen1, capsys): # pylint: disable=unused-argument
        gen1.header()
        p = gen1.dest.tell()
        gen1.footer()
        # out, err = capsys.readouterr()
        assert gen1.dest.getvalue()[p:] == """\
      }
    }
  }
}
@enduml
"""
class Test_TreeVisitor(object):
    def test_init(self):
        visitor = TreeVisitor(ast.Module())
        assert visitor

    def py2puml(self, sourcefile):
        gen = PUML_Generator(sourcefile, dest=io.StringIO(), package='')
        with open(sourcefile) as f:
            tree = ast.parse(f.read())
        visitor = TreeVisitor(gen)
        visitor.visit(tree)
        return gen.dest.getvalue()

    def test_visit(self):
        puml = self.py2puml('examples/person.py')
        assert puml == "class Person {\n" \
                       "  +firstname\n" \
                       "  +lastname\n" \
                       "  -__init__()\n" \
                       "  +Name()\n" \
                       "}\n" \
                       "Person <|-- Employee\n" \
                       "class Employee {\n" \
                       "  +staffnumber\n" \
                       "  -__init__()\n" \
                       "  +GetEmployee()\n" \
                       "}\n"
