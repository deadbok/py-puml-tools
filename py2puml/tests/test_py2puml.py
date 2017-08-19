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
def gen_no_ns():
    dest = io.StringIO()
    return PUML_Generator('some/sub/path/module.py', dest=dest)

@pytest.fixture
def gen_with_ns():
    dest = io.StringIO()
    return PUML_Generator('some/sub/path/module.py', dest=dest, root='.')

class Test_PUML_Generator_noNS(object):
    def test_init(self, gen_no_ns):
        assert gen_no_ns.namespaces == []
        assert gen_no_ns.depth == 0

    def test_header(self, gen_no_ns):
        assert gen_no_ns.tabs == 0
        gen_no_ns.header()
        assert gen_no_ns.tabs == 0
        assert gen_no_ns.dest.tell() == 80
        assert gen_no_ns.dest.getvalue() == """\
@startuml
skinparam monochrome true
skinparam classAttributeIconSize 0
scale 2

"""

    def test_footer(self, gen_no_ns):
        gen_no_ns.header()
        p = gen_no_ns.dest.tell()
        gen_no_ns.footer()
        assert gen_no_ns.dest.getvalue()[p:] == "@enduml\n"

class Test_PUML_Generator_NS(object):
    def test_init(self, gen_with_ns):
        assert gen_with_ns.namespaces == ['some', 'sub', 'path', 'module']
        assert gen_with_ns.depth == 4

    def test_header(self, gen_with_ns):
        # initially no indentation
        assert gen_with_ns.tabs == 0
        gen_with_ns.header()
        # generating header increases indentation
        assert gen_with_ns.tabs == gen_with_ns.depth
        assert gen_with_ns.dest.tell() == 161
        assert gen_with_ns.dest.getvalue() == """\
@startuml
skinparam monochrome true
skinparam classAttributeIconSize 0
scale 2

namespace some {
  namespace sub {
    namespace path {
      namespace module {
"""

    def test_footer(self, gen_with_ns):
        gen_with_ns.header()
        p = gen_with_ns.dest.tell()
        gen_with_ns.footer()
        assert gen_with_ns.dest.getvalue()[p:] == """\
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
        gen = PUML_Generator(sourcefile, dest=io.StringIO(), root='')
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
