"""Tests for py2puml (pytest)"""
# pylint: disable=invalid-name, missing-docstring

from py2puml import run, cli_parser
from version import __version__

def test_cli_usage(capsys):
    cli_parser().print_help()
    with open('examples/usage.txt') as f:
        expected = f.read()

    # Replace version number
    s = "py2puml v1.0.0\n"
    p = expected.find(s)
    q = p+len(s)
    expected = (expected[:p] + "py2puml v" + __version__ + "\n" + expected[q:])

    # compare with captured output
    out, err = capsys.readouterr()
    assert err == ''
    assert expected == out

def test_run_multiple_sources(capsys):
    args = cli_parser().parse_args(
        '--root . py2puml.py puml_generator.py code_info.py ast_visitor.py'.split())
    assert args.root == '.'
    assert args.py_file == ['py2puml.py', 'puml_generator.py', 'code_info.py', 'ast_visitor.py']
    assert args.root == '.'
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    assert out.count('namespace ') == 4
    assert out.count('class ') == 5

    with open('examples/py2puml_NS.puml') as f:
        expected = f.read()
    assert expected == out

def test_run_dbpuml2sql(capsys):
    args = cli_parser().parse_args(['-c', 'examples/dbpuml2sql.ini',
                                    #'-r', '../dbpuml2sql',
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

    assert expected == out

def test_run_dbsql2puml(capsys):
    args = cli_parser().parse_args(['-c', 'examples/dbsql2puml.ini',
                                    # '-r', '../dbsql2puml',
                                    '../dbsql2puml/dbsql2puml.py',
                                    '../dbsql2puml/sql2puml.py',
                                    '../dbsql2puml/sqlparsetables.py'])
    # FIXME include package name for base classes imported directly
    run(args)
    out, err = capsys.readouterr()

    assert err == ''
    # assert out.count('namespace ') == 0 # 6
    # assert out.count('{static}') == 1
    # assert out.count('class ') == 3
    # assert out.count('PUMLReader o-- Table') == 1

    with open('examples/dbsql2puml.puml') as f:
        expected = f.read()
    assert expected == out

def test_run_syntax_error(capsys):
    args = cli_parser().parse_args('examples/bugged.py examples/person.py'.split())
    run(args)
    out, err = capsys.readouterr()

    with open('examples/person.puml') as f:
        expected = f.read()
    assert expected == out

    assert err == """\
Syntax error in examples/bugged.py:6:57: while i<10 #Begin loop, repeat until there's ten numbers
Skipping file
"""

def test_run_filenotfound_error(capsys):
    args = cli_parser().parse_args('missing.py examples/person.py'.split())
    run(args)
    out, err = capsys.readouterr()

    with open('examples/person.puml') as f:
        expected = f.read()
    assert expected == out

    assert err == """\
[Errno 2] No such file or directory: 'missing.py', skipping
Skipping file
"""
