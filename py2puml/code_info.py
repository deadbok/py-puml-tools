"""

TODO : how to use ast Attributes
https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Attribute

>>> node = ast.parse('os.path.sep').body[0]
>>> ast.dump(node)
"Expr(value=Attribute(value=Attribute(value=Name(id='os', ctx=Load()), attr='path', ctx=Load()), attr='sep', ctx=Load()))"
>>> l =['node.value.value.value.id', 'node.value.value.attr', 'node.value.attr']
>>> [eval(e) for e in l]
['os', 'path', 'sep']
>>> astor.to_source(node)
'os.path.sep\n'

So
  - node is an Expr
  - node.value is an Attribute
  - Attribute nodes have a .value (node) and an .attr
  - the .value can be a Name or an Attribute
"""
import logging
import ast

logger = logging.getLogger(__name__)

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
        self.functions.append(node)

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
        return self.variables

    @property
    def methods(self):
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
        self.add_function(node)

    def done(self, context):
        "Signals end of class parsing."
        context.print_classinfo(self)
