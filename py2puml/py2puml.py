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
import ast
__VERSION__ = '0.1.9'
TAB = '  '

class ClassDef:
    """
    The parsed class definition.

    Elements are grouped by type in arrays while parsing, printing done last.
    """
    def __init__(self, node):
        self.classname = node.name
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
        "Registers an instance variable"
        self.members.append(name)

    def add_method(self, node):
        "Registers a method"
        self.methods.append(node)

    def done(self, context):
        "Signals end of class parsing."
        context.print_classdef(self)

class TreeVisitor(ast.NodeVisitor):
    """`ast.NodeVisitor` is the primary tool for ‘scanning’ the tree.
    To use it, subclass it and override methods visit_Foo, corresponding to the
    node classes (see Meet the Nodes).
    """
    # List to put the class data.
    def __init__(self, context=None):
        self.context = context
        self.classdef = None
        self.constructor = False

    def visit_ClassDef(self, node):
        """
        Overrides AST class definition visitor.

        :param node: The node of the class.
        """
        # push context
        prev_classdef = self.classdef
        self.classdef = ClassDef(node)

        # Run through all children of the class definition.
        for child in node.body:
            self.visit(child)

        # finished class parsing, report it now.
        self.classdef.done(self.context)

        # restore previous context
        self.classdef = prev_classdef

    def visit_FunctionDef(self, node):
        "Overrides AST function definition visitor"
        if self.classdef:
            # Check if this s the constructor.
            if node.name == '__init__':
                self.constructor = True
                # Find all assignment expressions in the constructor.
                for code in node.body:
                    self.visit(code)
                self.constructor = False
            self.classdef.add_method(node)

    def visit_Assign(self, node):
        "Overrides AST assignment statement visitor"
        if self.constructor:
            # Find attributes since we want "self." + "something"
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    # If the value is a name and its id is self.
                    if isinstance(target.value, ast.Name):
                        if target.value.id == 'self':
                            self.classdef.add_member(target.attr)

        elif self.classdef:
            # Look for class variables (shared by all instances)
            for target in node.targets:
                # Get the target member name.
                if isinstance(target, ast.Name):
                    self.classdef.add_classvar(target.id)

class PUML_Generator:
    "Formats data for PlantUML."
    def __init__(self, sourcename, dest, package=''):
        self.dest = dest
        self.tabs = 0

        # make namespace hierarchy from package or path
        names = sourcename.lstrip('./').split('/')
        if package != '':
            self.namespaces = package.rstrip('.').split('.')
        else:
            self.namespaces = names[:-1]
        modname = names[-1].split('.')[0]
        self.namespaces.append(modname)

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


    def print_classdef(self, classdef):
        """Prints class definition as plantuml script."""
        # TODO show base classes
        self.indent("class", classdef.classname, "{")
        self.tabs += 1
        for m in classdef.classvars:
            self.indent("{static}", classdef.visibility(m) + m)
        for m in classdef.members:
            self.indent(classdef.visibility(m) + m)
        for m in classdef.methods:
            # TODO print args (inspect signature ?)
            self.indent(classdef.visibility(m.name) + m.name + "()")
        self.tabs -= 1
        self.indent("}")

def cli_parser():
    "Builds a command line parser suitable for this tool."
    import argparse

    # Takes a python file as a parameter.
    parser = argparse.ArgumentParser(description='py2puml' +
                                     ' v{}'.format(__VERSION__) +
                                     ' by Martin B. K. Grønholdt' +
                                     ' and Michelle Baert'
                                     '\nCreate PlantUML classes' +
                                     ' from Python source code.')
    parser.add_argument('py_file', type=argparse.FileType('r'),
                        help='The Python source file to parse.')
    parser.add_argument('puml_file', type=argparse.FileType('w'),
                        help='The name of the ouput PlantUML file.')
    parser.add_argument('--package', default='', dest='package',
                        help='The package that the input file belongs to.')
    return parser

if __name__ == '__main__':

    cl_args = cli_parser().parse_args()
    try:
        # Use AST to parse the file.
        tree = ast.parse(cl_args.py_file.read())
        gen = PUML_Generator(cl_args.py_file.name, package=cl_args.package, dest=cl_args.puml_file)
        gen.header()
        visitor = TreeVisitor(gen)
        visitor.visit(tree)
        gen.footer()

    except SyntaxError as see:
        print('Syntax error in ', end='')
        print(cl_args.py_file.name + ':' + str(see.lineno) + ':' + str(
            see.offset) + ': ' + see.text)
    except BaseException as err:
        print(err)
