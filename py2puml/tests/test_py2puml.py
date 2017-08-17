"""Tests for py2puml (pytest)"""
import io
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring
# pylint  disable=unused-wildcard-import, redefined-outer-name
from py2puml import ClassDef, TreeVisitor, PUML_Generator


class Test_ClassDef(object):
    def test_visibility(self):
        assert ClassDef.visibility('__builtin__') == '-'
        assert ClassDef.visibility('_private') == '-'
        assert ClassDef.visibility('public') == '+'

    def test_init(self):
        pass
        #cdef = ClassDef()

    def test_add_member(self):
        pass
        #cdef = ClassDef()
        #cdef.add_member('member')
        #assert cdef.members == ['member']

class Test_TreeVisitor(object):
    pass

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
