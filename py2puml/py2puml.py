#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):

# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
"""
Program to parse Python classes and write their info to PlantUML files
(see http://plantuml.com/) that can be used to generate UML files and GraphViz
renderings of classes.

Missing:
 * Inheritance parsing
"""
# pylint: disable=C0103

# standard lib imports
import ast
import configparser
import logging
import logging.config
import os
import sys

# other imports
import yaml

# this project imports
from version import __version__
from puml_generator import PUML_Generator, PUML_Generator_NS
from code_info import CodeInfo, ClassInfo

HOME_DIR = os.path.dirname(__file__)

# puml indentation unit
TAB = '  '

# list of possible configuration files,
# all existing will be loaded unless a specific config arg is provided
CONFIG_FILENAMES = (
    os.path.join(HOME_DIR, 'py2puml.ini'),
    os.path.expanduser('~/.config/py2puml.ini'),
    os.path.expanduser('~/.py2puml.ini'),
    '.py2puml.ini',
    'py2puml.ini',
)
LOGGING_CFG = os.path.join(HOME_DIR, 'logging.yaml')

with open(LOGGING_CFG) as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger(__name__)

class TreeVisitor(ast.NodeVisitor):
    """`ast.NodeVisitor` is the primary tool for ‘scanning’ the tree.
    To use it, subclass it and override methods visit_Foo, corresponding to the
    node classes (see Meet the Nodes).
    """
    # List to put the class data.
    def __init__(self, context=None):
        self.context = context
        self.classinfo = None
        self.globals = CodeInfo()
        self.constructor = False

    def visit_ClassDef(self, node):
        """
        Overrides AST class definition visitor.

        :param node: The node of the class.
        """
        # push context
        prev_classinfo = self.classinfo
        self.classinfo = ClassInfo(node)

        # Run through all children of the class definition.
        for child in node.body:
            self.visit(child)

        # finished class parsing, report it now.
        self.classinfo.done(self.context)

        # restore previous context
        self.classinfo = prev_classinfo

    def visit_FunctionDef(self, node):
        "Overrides AST function definition visitor"
        if self.classinfo:
            # Check if this s the constructor.
            if node.name == '__init__':
                self.constructor = True
                # Find all assignment expressions in the constructor.
                for code in node.body:
                    self.visit(code)
                self.constructor = False
            self.classinfo.add_method(node)
        else:
            self.globals.add_function(node)

    def visit_Assign(self, node):
        "Overrides AST assignment statement visitor"
        # FIXME assignments to imported names may incorrectly report variable declaration
        # pylint: disable=unnecessary-lambda
        if self.constructor:
            # Find attributes since we want "self." + "something"
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    # If the value is a name and its id is self.
                    if isinstance(target.value, ast.Name):
                        if target.value.id == 'self':
                            self.classinfo.add_member(target.attr)
        else:
            if self.classinfo:
                # Store as class variable (shared by all instances)
                fn = lambda x: self.classinfo.add_classvar(x)
            else:
                # Store as global variable
                fn = lambda x: self.globals.add_variable(x)
                # pylint disable=unnecessary-lambda
            for target in node.targets:
                # keep only simple names
                if isinstance(target, ast.Name):
                    fn(target.id)


def cli_parser():
    "Builds a command line parser suitable for this tool."
    import argparse

    # Takes a python file as a parameter.
    parser = argparse.ArgumentParser(
        prog='py2uml',
        description='py2puml' +
        ' from Martin B. K. Grønholdt, v' + __version__ + ' by Michelle Baert.\n' +
        'Create PlantUML classes from Python source code.',
        epilog='If no config file is provided, settings are loaded \n' +
        'sequentially from all available files in :\n' +
        '      - <PROGRAM_DIR>/py2puml.ini\n' +
        '      - <USER_HOME>/.config/py2puml.ini\n' +
        '      - <USER_HOME>/.py2puml.ini\n' +
        '      - <WORK_DIR>/.py2puml.ini\n' +
        '      - <WORK_DIR>/py2puml.ini\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config',
                        help='Configuration file (replace defaults)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='The name of the ouput PlantUML file.')
    parser.add_argument('-r', '--root', #default='',
                        help='Project root directory.'
                        ' Create namespaces from there')
    parser.add_argument('py_file', nargs='+',
                        help='the Python source files to parse.')
    return parser

def run(cl_args):
    """Main application runner.

    @param cl_args: argparser namespace.
    """
    cfg = configparser.ConfigParser()
    # provided config file completely replaces global settings
    if cl_args.config:
        cfg.read(cl_args.config)
    else:
        cfg.read(CONFIG_FILENAMES)

    # setup .puml generator
    if cl_args.root:
        gen = PUML_Generator_NS(dest=cl_args.output,
                                root=cl_args.root,
                                config=cfg)
    else:
        gen = PUML_Generator(dest=cl_args.output,
                             config=cfg)

    # The tree visitor will use it
    visitor = TreeVisitor(gen)

    gen.header()
    for srcfile in cl_args.py_file:
        # Use AST to parse the file.
        try:
            with open(srcfile) as src:
                tree = ast.parse(src.read())
        except FileNotFoundError as err:
            sys.stderr.write(str(err) + ", skipping\n")
            continue
        except SyntaxError as see:
            sys.stderr.write('Syntax error in {0}:{1}:{2}: {3}'.format(
                srcfile, see.lineno, see.offset, see.text))
            sys.stderr.write("Aborting conversion of " + srcfile + "\n")
            # skip to next srcfile
            continue
        # Build output while walking the tree
        gen.start_file(srcfile)
        visitor.visit(tree)
        gen.end_file(srcfile)

    gen.footer()
    # TODO detect and warn about empty results
    # TODO optionally include global objects in a pseudo-class
    if cl_args.output != sys.stdout: # pragma: no cover
        cl_args.output.close()

if __name__ == '__main__': # pragma: no cover
    run(cli_parser().parse_args())
