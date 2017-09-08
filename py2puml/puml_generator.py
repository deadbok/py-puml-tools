"""PlantUML script generators.
"""
# pylint: disable=invalid-name

# standard lib imports
import ast
import copy
import logging
import os

# other imports
import astor
from ast_visitor import TreeVisitor

# puml printation unit
TAB = '  '
# module logger
logger = logging.getLogger() # (__name__)

class PUML_Generator:
    """Formats data for PlantUML.
    """
    def __init__(self, dest, config=None):
        """Constructor.

        @param dest stream : File-like object to write to
        @param config ConfigParser : custom settings (default None)
        """
        self.dest = dest
        self.config = config
        self.sourcename = None

    def opt_prolog(self):
        """Configured prolog for the PlantUML output.
        @return prolog string (defaulting to empty string) or False if no configuration available.
        """
        return self.config and self.config.get(
            'puml', 'prolog', fallback='')

    def opt_epilog(self):
        """Configured epilog for the PlantUML output.
        @return epilog string (defaulting to empty string) or False if no configuration available.
        """
        return self.config and self.config.get(
            'puml', 'epilog', fallback='')

    def opt_globals(self):
        """Tells whether the module globals should be reported.
        @return boolean
        """
        return self.config and self.config.getboolean(
            'module', 'write-globals', fallback=False)

    def opt_omit_self(self):
        """Tells whether the methods argument lists should include 'self'.
        This option could be useful to reduce classes width in diagram.
        @return boolean, False by default
        """
        return self.config and self.config.getboolean(
            'methods', 'omit-self', fallback=False)

    def opt_write_arglist(self, section='methods'):
        """Tells whether functions and methods argument lists be included.
        This option could be useful to reduce classes width in diagram.
        @return boolean, True by default
        """
        return not self.config or self.config.getboolean(
            section, 'write-arg-list', fallback=True)

    def opt_omit_defaults(self, section='methods'):
        """Tells whether default values should be omitted in functions and methods argument.
        This option could be useful to reduce classes width in diagram.
        @return boolean, False by default
        """
        return self.config and self.config.getboolean(
            section, 'omit-defaults', fallback=False)

    def start_file(self, sourcename):
        """Sets up the output context for a single python source file"""
        self.sourcename = sourcename

    def end_file(self, sourcename=None):
        """Cleans up the output context for a single python source file"""
        logger.info('finished with %s', sourcename)
        self.sourcename = None

    def output(self, *args):
        """Prints given arguments to destination.
        Override this for more formatting control.

        @param *args: arguments to be passed to the print() function.
        """
        print(*args, file=self.dest)

    def header(self):
        """Outputs file header: settings and namespaces."""
        self.output("@startuml")
        if self.config:
            prolog = self.config.get('puml', 'prolog', fallback=None)
            if prolog:
                self.output(prolog + "\n")

    def footer(self):
        """Outputs file footer.

        Prints configured epilog if exists and close puml section marker.
        """
        # append the epilog if provided
        if self.config:
            epilog = self.config.get('puml', 'epilog', fallback=None)
            if epilog:
                self.output(epilog + "\n")

        # End the PlantUML files.
        self.output('@enduml')

    def do_file(self, srcfile, errormsg=None):
        """Processes a single python source file,
           building output as configured while walking the tree.
        """
        # The tree visitor will use it
        visitor = TreeVisitor(srcfile, self)
        if visitor.parse(errormsg):
            self.start_file(srcfile)
            visitor.visit_tree()
            self.end_file()

    @staticmethod
    def _deco_marker(dec):
        """helper function for functions decorators"""
        if isinstance(dec, ast.Attribute):
            return '@' + astor.to_source(dec).rstrip()
        if dec.id == 'staticmethod':
            return 'static'
        if dec.id == 'abstractmethod':
            return 'abstract'
        return '@' + dec.id

    @staticmethod
    def is_static_method(meth):
        """Tells if given method is marked as static."""
        for dec in meth.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == 'staticmethod':
                return True

    def print_classinfo(self, classinfo):
        """Prints class definition as plantuml script."""
        for base in classinfo.bases:
            expr = astor.to_source(base).rstrip()
            # ignore base if 'object'
            if expr != 'object':
                self.output(expr, "<|--", classinfo.classname)
        # class and instance members
        self.output("class", classinfo.classname, "{")
        for m in classinfo.classvars:
            self.output(TAB + "{static}", classinfo.visibility(m) + m)
        for m in classinfo.members:
            self.output(TAB + classinfo.visibility(m) + m)
        for m in classinfo.methods:
            self.output(TAB + "{0}{1}({2}){3}".format(
                classinfo.visibility(m.name),
                m.name, self.arglist(m, ismethod=True),
                ','.join(["{%s}" % (self._deco_marker(dec),) for dec in m.decorator_list])
            ))
        self.output("}\n")

    def print_codeinfo(self, codeinfo):
        """Prints module globals as plantuml script."""
        assert self.opt_globals()
        # logger.warning("module.write-globals is not implemented")
        # represents data as a special class in plantuml
        self.output("class", "__module__", "{")
        for name in codeinfo.variables:
            self.output(TAB + codeinfo.visibility(name) + name)
        for fdef in codeinfo.functions:
            self.output(TAB + "{0}{1}({2})".format(
                codeinfo.visibility(fdef.name),
                fdef.name, self.arglist(fdef)))
        self.output("}\n")

    def arglist(self, fdef, ismethod=False):
        """Builds the argument list string of a function or method,
        according to configured options."""
        section = 'methods' if ismethod else 'module'
        if not self.opt_write_arglist(section):
            return ''

        # avoid changing orginal args
        args = copy.deepcopy(fdef.args)

        # omit-self ?
        if ismethod and self.opt_omit_self() and not self.is_static_method(fdef):
            self_arg = args.args.pop(0)
            if self_arg.arg != 'self':
                logger.warning("Unexpected name %r for method 'self' parameter in %s()",
                               self_arg.arg, fdef.name)

        # omit-defaults ?
        if self.opt_omit_defaults(section):
            args.defaults = []
            args.kw_defaults = []

        return astor.to_source(args).rstrip()

class PUML_Generator_NS(PUML_Generator):
    """Formats data for PlantUML.
    """
    def __init__(self, dest, root, config=None):
        super().__init__(dest, config)
        self.root = root
        self.namespaces = []

    @property
    def depth(self):
        """Levels of current namespace nesting"""
        return len(self.namespaces)

    def start_file(self, sourcename):
        """Sets up the output context for a single python source file.
        This is where namespaces nesting is generated.
        """
        super().start_file(sourcename)

        # make namespace hierarchy from root if supplied
        names = os.path.splitext(os.path.relpath(sourcename, self.root))[0]
        namespaces = names.split(os.path.sep)

        # determine the common path
        n = 0
        for d in self.namespaces:
            if n >= len(namespaces):
                break
            if d != namespaces[n]:
                break
            n += 1
        self.pop_ns(len(self.namespaces) - n)

        for d in namespaces[n:]:
            self.push_ns(d)

    def pop_ns(self, count=1):
        """Removes some inner namespaces"""
        for n in range(count): # pylint: disable=unused-variable
            self.namespaces.pop()
            self.output('}')

    def push_ns(self, name):
        """Adds an inner namespace to the context"""
        self.output('namespace ' + name + ' {')
        self.namespaces.append(name)

    def output(self, *args):
        """Formats given arguments to destination with proper indentation."""
        if self.namespaces:
            print(TAB * self.depth, end="", file=self.dest)
        super().output(*args)

    def footer(self):
        """Outputs file footer: close namespaces and marker."""
        # Close the namespaces
        while self.namespaces:
            self.pop_ns(self.depth)
        super().footer()
