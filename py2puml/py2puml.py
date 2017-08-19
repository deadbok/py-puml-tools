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
import logging
import logging.config
import os
import sys

# other imports
import astor
import yaml

__VERSION__ = '0.2.0'
TAB = '  '

# logging.basicConfig(level='DEBUG', filename="py2puml.log", filemode='w')
# logging.config.fileConfig('logging.conf')
with open('logging.yaml') as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger(__name__)

class ClassInfo:
    """
    The parsed class definition.

    Elements are grouped by type in arrays while parsing, printing done last.
    """
    def __init__(self, node):
        self.classname = node.name
        self.bases = node.bases
        self.classvars = []
        self.members = []
        self.methods = []

    @staticmethod
    def visibility(name):
        """Detects the visibility of given member name, as plantuml convention symbol.

       @returns '-' for private, '+' for public
        """
        if name.startswith('_'):
            return '-'
        return '+'

    def add_classvar(self, name):
        "Registers a class variable"
        self.classvars.append(name)

    def add_member(self, name):
        "Registers an instance variable if new"
        if name not in self.members:
            self.members.append(name)

    def add_method(self, node):
        "Registers a method"
        self.methods.append(node)

    def done(self, context):
        "Signals end of class parsing."
        context.print_classinfo(self)

class TreeVisitor(ast.NodeVisitor):
    """`ast.NodeVisitor` is the primary tool for ‘scanning’ the tree.
    To use it, subclass it and override methods visit_Foo, corresponding to the
    node classes (see Meet the Nodes).
    """
    # List to put the class data.
    def __init__(self, context=None):
        self.context = context
        self.classinfo = None
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

    def visit_Assign(self, node):
        "Overrides AST assignment statement visitor"
        if self.constructor:
            # Find attributes since we want "self." + "something"
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    # If the value is a name and its id is self.
                    if isinstance(target.value, ast.Name):
                        if target.value.id == 'self':
                            self.classinfo.add_member(target.attr)

        elif self.classinfo:
            # Look for class variables (shared by all instances)
            for target in node.targets:
                # Get the target member name.
                if isinstance(target, ast.Name):
                    self.classinfo.add_classvar(target.id)

class PUML_Generator:
    "Formats data for PlantUML."
    def __init__(self, sourcename, dest, root=''):
        self.dest = dest
        self.tabs = 0

        # make namespace hierarchy from root if supplied
        if root:
            names = os.path.splitext(os.path.relpath(sourcename, root))[0]
            self.namespaces = names.split(os.path.sep)
        else:
            self.namespaces = []

    @property
    def depth(self):
        "Levels of current namespace nesting"
        return len(self.namespaces)

    def indent(self, *args):
        "Formats given arguments to destination with proper indentation."
        if self.tabs:
            print(TAB * self.tabs, end="", file=self.dest)
        print(*args, file=self.dest)

    def header(self):
        "Outputs file header: settings and namespaces."
        self.indent("@startuml\n"
                    "skinparam monochrome true\n"
                    "skinparam classAttributeIconSize 0\n"
                    "scale 2\n")

        # Create the namespaces
        for name in self.namespaces:
            self.indent('namespace ' + name + ' {')
            self.tabs += 1

    def footer(self):
        "Outputs file footer: close namespaces and marker."
        # Close the namespaces
        while self.tabs > 0:
            self.tabs -= 1
            self.indent('}')

        # End the PlantUML files.
        self.indent('@enduml')


    def print_classinfo(self, classinfo):
        """Prints class definition as plantuml script."""
        for base in classinfo.bases:
            expr = astor.to_source(base).rstrip()
            # ignore base if 'object'
            if expr != 'object':
                self.indent(expr, "<|--", classinfo.classname)
        # class and instance members
        self.indent("class", classinfo.classname, "{")
        self.tabs += 1
        for m in classinfo.classvars:
            self.indent("{static}", classinfo.visibility(m) + m)
        for m in classinfo.members:
            self.indent(classinfo.visibility(m) + m)
        for m in classinfo.methods:
            logger.info("Method: %r \n%s", m, ast.dump(m))
            arglist = astor.to_source(m.args).rstrip()
            self.indent("{0}{1}({2})".format(classinfo.visibility(m.name),
                                             m.name, arglist))
        self.tabs -= 1
        self.indent("}\n")

def cli_parser():
    "Builds a command line parser suitable for this tool."
    import argparse

    # Takes a python file as a parameter.
    parser = argparse.ArgumentParser(prog='py2uml',
                                     description='py2puml' +
                                     ' v{}'.format(__VERSION__) +
                                     ' by Martin B. K. Grønholdt' +
                                     ' and Michelle Baert'
                                     '\nCreate PlantUML classes' +
                                     ' from Python source code.')
    parser.add_argument('py_file', type=argparse.FileType('r'),
                        help='The Python source file to parse.')
    parser.add_argument('puml_file', type=argparse.FileType('w'),
                        nargs='?', default=sys.stdout,
                        help='The name of the ouput PlantUML file.')
    parser.add_argument('--root', #default='',
                        help='Project root directory.'
                        ' Create namespaces from there')
    return parser

if __name__ == '__main__':

    cl_args = cli_parser().parse_args()
    try:
        # Use AST to parse the file.
        tree = ast.parse(cl_args.py_file.read())
        cl_args.py_file.close()

        # setup .puml generator
        gen = PUML_Generator(cl_args.py_file.name,
                             dest=cl_args.puml_file,
                             root=cl_args.root)

        # The tree visitor will use it
        visitor = TreeVisitor(gen)

        # Build output while walking the tree
        gen.header()
        visitor.visit(tree)
        gen.footer()

    except SyntaxError as see:
        print('Syntax error in ', end='')
        print(cl_args.py_file.name + ':' + str(see.lineno) + ':' + str(
            see.offset) + ': ' + see.text)
    # except BaseException as err:
    #     print(err)
