"""PlantUML script generators.
"""
# pylint: disable=invalid-name

# standard lib imports
import logging
import os

# other imports
import astor

# puml printation unit
TAB = '  '
# module logger
logger = logging.getLogger(__name__)

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
            # TODO allow to disable or simplify arg lists output (config)
            arglist = astor.to_source(m.args).rstrip()
            self.output(TAB + "{0}{1}({2})".format(
                classinfo.visibility(m.name),
                m.name, arglist))
        self.output("}\n")

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
        """Sets up the output context for a single python source file"""
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
