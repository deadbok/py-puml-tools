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
        assert gen.dest.getvalue()[p:] == """@enduml\n"""

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
@enduml
"""
    def test_folder_tree(self, gen):
        sources = ['setup.py',
                   'sample/module1.py',
                   'dirA1/dirB1/module2.py',
                   'dirA1/module3.py',
                   'dirA2/dir_and_module/module4.py',
                   'dirA2/dir_and_module.py',
                   'dirA3/some/other/module4.py']
        for src in sources:
            ns = src[:-3].split('/')
            gen.start_file(src)
            assert gen.depth == len(ns)
            assert gen.namespaces == ns
            gen.output("# contents of", src)
            gen.end_file()
        gen.footer() # close all namespaces
        assert gen.dest.getvalue() == """\
namespace setup {
  # contents of setup.py
}
namespace sample {
  namespace module1 {
    # contents of sample/module1.py
  }
}
namespace dirA1 {
  namespace dirB1 {
    namespace module2 {
      # contents of dirA1/dirB1/module2.py
    }
  }
  namespace module3 {
    # contents of dirA1/module3.py
  }
}
namespace dirA2 {
  namespace dir_and_module {
    namespace module4 {
      # contents of dirA2/dir_and_module/module4.py
    }
    # contents of dirA2/dir_and_module.py
  }
}
namespace dirA3 {
  namespace some {
    namespace other {
      namespace module4 {
        # contents of dirA3/some/other/module4.py
      }
    }
  }
}
@enduml
"""
    #TODO test static methods

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

def test_run_multiple_sources(capsys):
    args = cli_parser().parse_args(
        '--root . py2puml.py puml_generator.py code_info.py'.split())
    assert args.root == '.'
    assert args.py_file == ['py2puml.py', 'puml_generator.py', 'code_info.py']
    assert args.root == '.'
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    assert out.count('namespace ') == 3
    assert out.count('class ') == 5

    with open('examples/py2puml_NS.puml') as f:
        expected = f.read()
    assert out == expected

def test_run_dbpuml2sql(capsys):
    args = cli_parser().parse_args(['-c', 'examples/dbpuml2sql.ini',
                                    #'-r', '..',
                                    '../dbpuml2sql/dbpuml2sql.py',
                                    '../dbpuml2sql/__init__.py',
                                    '../dbpuml2sql/pumlreader.py',
                                    '../dbpuml2sql/table.py',
                                    '../dbpuml2sql/test_Table.py'])
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    assert out.count('namespace ') == 0 # 6
    assert out.count('{static}') == 1
    assert out.count('class ') == 3
    assert out.count('PUMLReader o-- Table') == 1

    with open('examples/dbpuml2sql.puml') as f:
        expected = f.read()
    assert out == expected

def test_run_dbspq2puml(capsys):
    args = cli_parser().parse_args(['-c', 'examples/dbsql2puml.ini',
                                    #'-r', '..',
                                    '../dbsql2puml/dbsql2puml.py',
                                    '../dbsql2puml/sql2puml.py',
                                    '../dbsql2puml/sqlparsetables.py'])
    # missing config file silently ignores any config. Call it a feature
    # FIXME include package name for base classes imported directly
    # FIXME relations between namespaces
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    # assert out.count('namespace ') == 0 # 6
    # assert out.count('{static}') == 1
    # assert out.count('class ') == 3
    # assert out.count('PUMLReader o-- Table') == 1

    with open('examples/dbsql2puml.puml') as f:
        expected = f.read()
    assert out == expected

def test_run_syntax_error(capsys):
    args = cli_parser().parse_args('examples/bugged.py examples/person.py'.split())
    run(args)
    out, err = capsys.readouterr()

    with open('examples/person.puml') as f:
        expected = f.read()
    assert out == expected

    assert err == """\
Syntax error in examples/bugged.py:6:57: while i<10 #Begin loop, repeat until there's ten numbers
Aborting conversion of examples/bugged.py
"""

def test_run_filenotfound_error(capsys):
    args = cli_parser().parse_args('missing.py examples/person.py'.split())
    run(args)
    out, err = capsys.readouterr()

    with open('examples/person.puml') as f:
        expected = f.read()
    assert out == expected

    assert err == """\
[Errno 2] No such file or directory: 'missing.py', skipping
"""
