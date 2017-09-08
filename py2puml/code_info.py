"""
Classes for managing infos and ast nodes about parsed python code.

Infos are fed by some ast.NodeVisitor and used by some PUML_Generator.
"""
import logging
import ast

logger = logging.getLogger() # (__name__) # pylint: disable=invalid-name

class CodeInfo:
    """
    Container for collecting information about various code elements .
    """
    def __init__(self):
        self.variables = []
        self.functions = []

    def add_variable(self, name):
        "Registers a global variable"
        if name not in self.variables:
            self.variables.append(name)

    def add_function(self, node):
        "Registers a function"
        # don't store unneeded body
        node.body = ast.Pass()
        self.functions.append(node)

    def done(self, context):
        "Signals end of module parsing."
        context.print_codeinfo(self)

    @staticmethod
    def visibility(name):
        """Detects the visibility of given member name, as plantuml convention symbol.

       @returns '-' for private, '+' for public
        """
        if name.startswith('_'):
            return '-'
        return '+'


class ClassInfo(CodeInfo):
    """
    The parsed class definition.

    Elements are grouped by type in arrays while parsing, printing done last.
    """
    def __init__(self, node):
        super().__init__()
        logger.info("New ClassInfo: %s", ast.dump(node))
        self.classname = node.name
        self.bases = node.bases
        # self.classvars = []
        self.members = []
        # self.methods = []

    @property
    def classvars(self):
        """The list of class variables.
        Class variables are shared by all instances."""
        return self.variables

    @property
    def methods(self):
        """The list of parsed methods of the class"""
        return self.functions

    def add_classvar(self, name):
        "Registers a class variable"
        self.add_variable(name)

    def add_member(self, name):
        "Registers an instance variable if new"
        if name not in self.members:
            self.members.append(name)

    def add_method(self, node):
        "Registers a method"
        node.body = None
        self.add_function(node)

    def done(self, context):
        "Signals end of class parsing."
        context.print_classinfo(self)
