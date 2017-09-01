"""Tests for code_info.py (pytest)"""
import ast
import configparser
import io
import pytest
# pylint: disable= invalid-name, redefined-outer-name, missing-docstring, no-self-use, too-few-public-methods

from puml_generator import PUML_Generator, PUML_Generator_NS

@pytest.fixture
def cfg():
    cfg = configparser.ConfigParser()
    cfg.read('py2puml.ini')
    return cfg

@pytest.fixture
def cfg_omit_self():
    cfg = configparser.ConfigParser()
    cfg.read_dict({'methods': {'omit-self: True'}})
    return cfg

@pytest.fixture
def cfg_omit_defaults():
    cfg = configparser.ConfigParser()
    cfg.read_dict({
        'module': {'omit-defaults: True'},
        'methods': {'omit-defaults: True'}
    })
    return cfg

@pytest.fixture
def cfg_write_globals():
    cfg = configparser.ConfigParser()
    cfg.read_string("""
    [module]
    write-globals = True
    """)
    return cfg

def gen_with_config(text_or_dict, cls=PUML_Generator):
    cfg = configparser.ConfigParser()
    if isinstance(text_or_dict, str):
        cfg.read_string(text_or_dict)
    else:
        # if isinstance(text_or_dict, dict)
        # if 'items' in dir(text_or_dict) and callable(text_or_dict.items)
        cfg.read_dict(text_or_dict)

    dest = io.StringIO()
    gen = cls(dest, config=cfg)
    return gen

def assert_match_file(gen, filename):
    # print a clean version of actual output, on failure
    print(gen.dest.getvalue())
    with open(filename) as f:
        expected = f.read()
    assert gen.dest.getvalue() == expected

# ======================================================================
def test_default_config(cfg):
    assert not cfg.getboolean('methods', 'omit-arg-list', fallback=False)
    assert not cfg.getboolean('methods', 'omit-self', fallback=False)
    assert not cfg.getboolean('methods', 'omit-defaults', fallback=False)
    with pytest.raises(configparser.NoOptionError, message="Expecting NoOptionError"):
        assert not cfg.getboolean('methods', 'unknown')

class Test_PUML_Generator(object):
    pyfilename = 'some/sub/path/module.py'

    @staticmethod
    @pytest.fixture
    def gen0():
        "A PUML_Generator instance with no config"
        dest = io.StringIO()
        return PUML_Generator(dest)

    @staticmethod
    @pytest.fixture
    def gen(cfg):
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

    def test_config_default(self, cfg):
        dest = io.StringIO()
        gen = PUML_Generator(dest, config=cfg)

        assert not gen.opt_globals()
        assert not gen.opt_omit_self()
        assert not gen.opt_omit_defaults()
        assert gen.opt_write_arglist()
        assert gen.opt_prolog()
        assert not gen.opt_epilog()

        gen.header()
        gen.do_file('examples/example.py')
        gen.footer()

        assert "namespace " not in gen.dest.getvalue()
        assert "global_func" not in gen.dest.getvalue()
        assert "(self, " in gen.dest.getvalue()
        assert "+cls_meth(){static}" in gen.dest.getvalue()
        # assert "skinparam " in gen.dest.getvalue()
        assert_match_file(gen, 'examples/example.puml')

    def test_config_none(self, gen0):
        gen = gen0
        gen.do_file('examples/example.py')
        assert "namespace " not in gen.dest.getvalue()
        assert "global_func" not in gen.dest.getvalue()
        assert "(self, " in gen.dest.getvalue()
        assert "skinparam " not in gen.dest.getvalue()
        # assert_match_file(gen, 'examples/example.puml')

    def test_write_arglist(self):
        gen = gen_with_config("""[methods]
        write-arg-list = False
        [module]
        write-globals = True
        """)
        gen.do_file('examples/example.py')
        assert "__init__()" in gen.dest.getvalue()
        assert "global_func(arg1, arg2, arg3=None)" in gen.dest.getvalue()

    def test_write_arglist2(self):
        gen = gen_with_config("""\
        [DEFAULT]
        write-arg-list = False
        [module]
        write-globals = True
        [methods]
        """)
        gen.do_file('examples/example.py')
        print(gen.dest.getvalue())
        assert "__init__()" in gen.dest.getvalue()
        assert "global_func()" in gen.dest.getvalue()

    def test_omit_self(self):
        gen = gen_with_config("""\
        [methods]
        omit-self = True
        """)
        assert gen.opt_omit_self()
        gen.do_file('examples/example.py')
        print(gen.dest.getvalue())
        assert "__init__(name, details={}, **kwargs)" in gen.dest.getvalue()

    def test_omit_defaults(self):
        gen = gen_with_config("""\
        [DEFAULT]
        omit-defaults = True
        [methods]
        [module]
        write-globals = True
        """)
        cfg = gen.config
        print({s:{o:v for o, v in cfg.items(s)} for s, o in cfg.items()})
        assert gen.opt_omit_defaults('methods')
        assert gen.opt_omit_defaults('module')
        gen.do_file('examples/example.py')
        print(gen.dest.getvalue())
        assert "__init__(self, name, details, **kwargs)" in gen.dest.getvalue()
        assert "global_func(arg1, arg2, arg3)" in gen.dest.getvalue()
        # assert False # force output

    def test_attribute_decorator(self):
        # pylint: disable=protected-access
        node = ast.parse(
            "import contextlib\n"
            "@contextlib.contextmanager\n"
            "def tag(name):\n"
            "    pass\n")
        import astor
        print(astor.dump_tree(node.body[1]))
        deco = PUML_Generator._deco_marker(node.body[1].decorator_list[0])
        assert deco == '@contextlib.contextmanager'

    def test_abstract(self):
        pass # included in example.py

    def test_badself(self, caplog):
        gen = gen_with_config("""\
        [methods]
        omit-self = True
        """)
        src = "class A:\n" \
              "    def meth(badself, arg1): pass\n"
        tree = ast.parse(src)
        fdef = tree.body[0].body[0]
        import logging
        with caplog.at_level(logging.WARNING):
            al = gen.arglist(fdef, True)
            assert al == "arg1"
            assert caplog.record_tuples == [
                ('root', logging.WARNING,
                 "Unexpected name 'badself' for method 'self' parameter in meth()")]

class Test_PUML_Generator_NS(object):
    pyfilename = 'some/sub/path/module.py'

    @staticmethod
    @pytest.fixture
    def gen():
        dest = io.StringIO()
        cfg = configparser.ConfigParser()
        cfg.read('py2puml.ini')
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
        print(gen.dest.getvalue())
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
    def test_write_globals(self, cfg_write_globals):
        dest = io.StringIO()
        gen = PUML_Generator_NS(dest, root='.', config=cfg_write_globals)
        gen.header()
        gen.do_file('examples/example.py')
        gen.footer()
        assert "global_func" in gen.dest.getvalue()
        assert_match_file(gen, 'examples/example_globals_NS.puml')


#TODO test bad config file
