"""Tests for using astor library (pytest)"""
import ast
import astor
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring, no-self-use, too-few-public-methods, line-too-long

assert astor.__version__ >= "0.6"

@pytest.fixture
def ast_class0():
    """AST tree of an empty class"""
    return astor.code_to_ast("class MyClass: pass").body[0]

@pytest.fixture
def ast_person():
    "Simple inheritance AST tree"
    # This is a very thin wrapper around ast.parse
    tree = astor.code_to_ast.parse_file('examples/person.py')
    return tree

@pytest.fixture
def ast_calendar():
    "Multiple inheritance AST tree"
    # This is a very thin wrapper around ast.parse
    tree = astor.code_to_ast.parse_file('examples/calendar_clock.py')
    return tree

def test_dump(ast_person):
    expected = "Module(\n" \
               "    body=[\n" \
               "        ClassDef(name='Person',\n" \
               "            bases=[],\n"
    ans = astor.dump_tree(ast_person)
    assert ans[:len(expected)] == expected

def test_to_source(ast_person):
    ans = astor.to_source(ast_person)
    # print(ansys
    assert len(ans) == 532

def test_simple_inheritance():
    # cdef = astor.code_to_ast("class MyClass (MyParent): pass").body[0]
    cdef = ast.parse("class MyClass (MyParent): pass").body[0]

    # ast and astor give different dump results:
    assert ast.dump(cdef) == "ClassDef(name='MyClass', bases=[Name(id='MyParent', ctx=Load())], keywords=[], body=[Pass()], decorator_list=[])"

    assert astor.dump_tree(cdef) == "ClassDef(name='MyClass', bases=[Name(id='MyParent')], keywords=[], body=[Pass], decorator_list=[])"

    # list bases:
    exprs = [astor.to_source(base).rstrip() for base in cdef.bases]
    assert exprs == ['MyParent']

def test_multiple_inheritance():
    # cdef = astor.code_to_ast("class MyClass (MyParent): pass").body[0]
    cdef = ast.parse("class MyClass (MyParent, OtherParent): pass").body[0]

    exprs = [astor.to_source(base).rstrip() for base in cdef.bases]
    assert exprs == ['MyParent', 'OtherParent']

def test_composite_inheritance():
    cdef = ast.parse("class MyClass (mypackage.MyParent): pass").body[0]

    exprs = [astor.to_source(base).rstrip() for base in cdef.bases]
    assert exprs == ['mypackage.MyParent']

def test_simple_arglist():
    fdef = ast.parse("def my_function(arg1,arg2,arg3=None): pass").body[0]

    # ast and astor give different dump results:
    assert ast.dump(fdef) == "FunctionDef(name='my_function', args=arguments(args=[arg(arg='arg1', annotation=None), arg(arg='arg2', annotation=None), arg(arg='arg3', annotation=None)], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[NameConstant(value=None)]), body=[Pass()], decorator_list=[], returns=None)"

    assert astor.dump_tree(fdef) == "FunctionDef(name='my_function',\n"\
        "    args=arguments(\n"\
        "        args=[arg(arg='arg1', annotation=None), arg(arg='arg2', annotation=None), arg(arg='arg3', annotation=None)],\n"\
        "        vararg=None,\n"\
        "        kwonlyargs=[],\n"\
        "        kw_defaults=[],\n"\
        "        kwarg=None,\n"\
        "        defaults=[NameConstant(value=None)]),\n"\
        "    body=[Pass],\n"\
        "    decorator_list=[],\n"\
        "    returns=None)"

    # list bases:
    expr = astor.to_source(fdef.args).rstrip()
    assert expr == 'arg1, arg2, arg3=None'

def test_complex_arg_list():
    """
    Example taken from https://greentreesnakes.readthedocs.io/en/latest/nodes.html#arg
    """
    code = "@dec1\n"\
           "@dec2\n"\
           "def f(a: 'annotation', b=1, c=2, *d, e, f=3, **g) ->'return annotation':\n"\
           "    pass\n"
    fdef = ast.parse(code)
    expr = astor.to_source(fdef)
    assert expr == code
    assert astor.to_source(fdef.body[0].args) == \
        "a: 'annotation', b=1, c=2, *d, e, f=3, **g\n"
