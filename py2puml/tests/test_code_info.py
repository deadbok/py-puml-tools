"""Tests for code_info.py (pytest)"""
import ast
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring, no-self-use, too-few-public-methods

from code_info import ClassInfo, CodeInfo

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


class TestCodeInfo(object):
    def test_init(self):
        o = CodeInfo()
        assert o

    def test_visibility(self):
        assert ClassInfo.visibility('__builtin__') == '-'
        assert ClassInfo.visibility('_private') == '-'
        assert ClassInfo.visibility('public') == '+'


class TestClassInfo(object):
    def test_init(self, ast_class1):
        print(ast.dump(ast_class1))
        cdef = ClassInfo(ast_class1)
        assert cdef.classname == "MyClass"

    def test_add_member(self, ast_class0):
        cdef = ClassInfo(ast_class0)
        cdef.add_member('member')
        assert cdef.members == ['member']
