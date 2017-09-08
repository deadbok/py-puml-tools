# pylint: disable=invalid-name
"""Custom Abstract Syntax Tree visitors"""

import ast
import logging
import sys
from code_info import CodeInfo, ClassInfo

logger = logging.getLogger() # (__name__)



class TreeVisitor(ast.NodeVisitor):
    """`ast.NodeVisitor` is the primary tool for ‘scanning’ the tree.
    To use it, subclass it and override methods visit_Foo, corresponding to the
    node classes (see Meet the Nodes).

    >>> visitor = TreeVisitor("examples/person.py")
    >>> visitor.parse(
    >>> visitor.visit_tree()

    """
    # List to put the class data.
    def __init__(self, srcfile, context=None):
        self.srcfile = srcfile
        self.context = context
        self.classinfo = None
        self.moduleinfo = None
        self.constructor = False
        self.tree = None

    def parse(self, errormsg=None):
        """Use AST to parse the source file."""
        try:
            with open(self.srcfile) as src:
                self.tree = ast.parse(src.read())
            return self.tree

        except FileNotFoundError as err:
            sys.stderr.write(str(err) + ", skipping\n")
        except SyntaxError as see:
            sys.stderr.write('Syntax error in {0}:{1}:{2}: {3}'.format(
                self.srcfile, see.lineno, see.offset, see.text))
        if errormsg:
            sys.stderr.write(errormsg + "\n")
        return False

    def visit_tree(self):
        """Visits the parsed tree."""
        return self.visit(self.tree)

    def visit_Module(self, node):
        """
        Overrides AST module visitor (top level).

        :param node ast.Node : The parsed code
        """
        # Instanciate moduleinfo if required
        # self.moduleinfo = context.getboolean(
        #     'module','write-globals', fallback=False) and CodeInfo() or None
        self.moduleinfo = CodeInfo() if self.context.opt_globals() else None

        # Run through all children of the module
        for child in node.body:
            self.visit(child)

        if self.moduleinfo:
            self.moduleinfo.done(self.context)


    def visit_ClassDef(self, node):
        """
        Overrides AST class definition visitor.

        :param node: The node of the class.
        """
        # push context
        prev_classinfo = self.classinfo
        self.classinfo = ClassInfo(node)

        # Run through all children of the class definition
        for child in node.body:
            self.visit(child)

        # finished class parsing, report it now.
        if self.classinfo:
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
        elif self.moduleinfo:
            self.moduleinfo.add_function(node)

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
            elif self.moduleinfo:
                # Store as global variable
                fn = lambda x: self.moduleinfo.add_variable(x)
                # pylint disable=unnecessary-lambda
            else:
                return
            for target in node.targets:
                # keep only simple names
                if isinstance(target, ast.Name):
                    fn(target.id)
