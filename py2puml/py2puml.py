#!/usr/bin/python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
# Program to parse Python classes and write their info to PlantUML files
# (see http://plantuml.com/) that can be used to generate UML files and GraphViz
# renderings of classes.
#
# Missing:
#  * Inheritance parsing
#  * Does not like end='' in print.
#
# History:
# Version 0.1.9
#  * Added package argument.
#
# Version 0.1.8
#  * Nicer command line help.
#
# Version 0.1.7
# * Fixed bug, when no namespace.
#
# Version 0.1.6
# * Functional namespace support
#
# Version 0.1.5
# * Add members from the class definition.
# * Do not write empty file.
# * Add namespace.
#
# Version 0.1.4
# * Output file name is now a parameter.
#
# Version 0.1.3
# * Change output file name to add ".db.puml" to the original file name.
#
# Version 0.1.2
#  * Exception handling.
#
# Version 0.1.1
#  * Comments.
#
# Version 0.1.0
#  * First working version.

import argparse
import ast

__VERSION__ = '0.1.9'


class ClassParser(ast.NodeVisitor):
    """
    Class to parse the stuff we're interested in from a class.

     * Methods and their visibility.
     * Members created in __init__ and their visibility.
    """
    # List to put the class data.
    puml_classes = list()

    def visit_ClassDef(self, node):
        """
        Class visitor that parses the info we want, when encountering a class definition.

        :param node: The node of the class.
        """
        # Dictionary containing the interesting parts of the classes structure
        puml_class = dict()
        puml_class['name'] = node.name
        puml_class['members'] = list()
        puml_class['methods'] = list()

        # Run through all children of the class definition.
        for child in node.body:
            # If we have a function definition, store it.
            if isinstance(child, ast.FunctionDef):
                # Check if it is "private".
                if child.name.startswith('__'):
                    puml_class['methods'].append('-' + child.name)
                else:
                    puml_class['methods'].append('+' + child.name)

                # Check if this s the constructor.
                if child.name == '__init__':
                    # Find all assignment expressions in the constructor.
                    for code in child.body:
                        if isinstance(code, ast.Assign):
                            # Find attributes since we want "self." + "something"
                            for target in code.targets:
                                if isinstance(target, ast.Attribute):
                                    # If the value is a name and its id is self.
                                    if isinstance(target.value, ast.Name):
                                        if target.value.id == 'self':
                                            # Check if it is "private".
                                            if target.attr.startswith('__'):
                                                puml_class['members'].append(
                                                    '-' + target.attr)
                                            else:
                                                puml_class['members'].append(
                                                    '+' + target.attr)

            # Look for assignments at the top level of the class.
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    # Get the target member name.
                    if isinstance(target, ast.Name):
                        # Append the member.
                        if target.id.startswith('__'):
                            puml_class['members'].append('-' + target.id)
                        else:
                            puml_class['members'].append('+' + target.id)

        # Save the class.
        self.puml_classes.append(puml_class)


if __name__ == '__main__':
    # Takes a python file as a parameter.
    parser = argparse.ArgumentParser(description='py2puml' +
                                                 ' v{}'.format(__VERSION__) +
                                                 ' by Martin B. K. Grønholdt' +
                                                 '\nCreate PlantUML classes' +
                                                 ' from Python source code.')
    parser.add_argument('py_file', type=argparse.FileType('r'),
                        help='The Python source file to parse.')
    parser.add_argument('puml_file', type=argparse.FileType('w'),
                        help='The name of the ouput PlantUML file.')
    parser.add_argument('--package', default='', dest='package',
                        help='The package that the input file belongs to.')
    args = parser.parse_args()

    try:
        # Use AST to parse the file.
        tree = ast.parse(args.py_file.read())
        class_writer = ClassParser()
        class_writer.visit(tree)


        names = args.py_file.name
        names = names.lstrip('./').split('/')[0:-1]

        if args.package != '':
            package = args.package.rstrip('.')
            namespace = package.split('.')
        else:
            namespace = []
            for name in names:
                namespace.append(name)

        if len(class_writer.puml_classes) > 0:
            tabs = 0
            # Write the beginnings of the PlantUML file.
            args.puml_file.write('{0}@startuml\n'.format('\t' * tabs))
            args.puml_file.write(
                '{0}skinparam monochrome true\n'.format('\t' * tabs))
            args.puml_file.write(
                '{0}skinparam classAttributeIconSize 0\n'.format('\t' * tabs))
            args.puml_file.write('{0}scale 2\n\n'.format('\t' * tabs))

            # Create the namespace
            if len(namespace) > 0:
                for name in namespace:
                    args.puml_file.write(
                        '{}namespace '.format('\t' * tabs) + name + ' {\n\n')
                    tabs += 1

            # Write the resulting classes in PlantUML format.
            for puml_class in class_writer.puml_classes:

                args.puml_file.write(
                    '{}class '.format('\t' * tabs) + puml_class[
                        'name'] + ' {\n')
                tabs += 1

                for member in puml_class['members']:
                    args.puml_file.write(
                        '{}'.format('\t' * tabs) + member + '\n')

                for method in puml_class['methods']:
                    args.puml_file.write(
                        '{}'.format('\t' * tabs) + method + '()\n')

                tabs -= 1
                args.puml_file.write('{}'.format('\t' * tabs) + '}\n\n')


            # Close the namespace
            if len(namespace) > 0:
                for name in namespace:
                    tabs -= 1
                    args.puml_file.write('{}'.format('\t' * tabs) + '}\n')

            # End the PlantUML files.
            args.puml_file.write('{}@enduml'.format('\t' * tabs))
            print('.'.join(namespace) + '.' + puml_class['name'] + ' ',
                      end='')
        else:
            print('No classes.', end='')
        print()

    except IOError:
        print('I/O error.')
    except SyntaxError as see:
        print('Syntax error in ', end='')
        print(args.py_file.name + ':' + str(see.lineno) + ':' + str(
            see.offset) + ': ' + see.text)
