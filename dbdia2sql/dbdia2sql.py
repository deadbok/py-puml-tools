#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
#
# Version 1.0.2 (2017-08-03)
#  * Fix help description.
#
# Version 1.0.1
#  * Few touch ups
#
# Version 1.0.0
#  * First working version.
#
"""
Name: dbdia2sql.py
Author: Martin Bo Kristensen Grønholdt.
Version 1.0.2 (2017-08-03)

Convert a database diagram written in a subset of PlantUML to SQLite syntax
that will create the actual tables and relations.
"""
from argparse import ArgumentParser
import argparse
import re

# Program version.
__VERSION__ = '1.0.2'


class Table:
    """
    Parses a table from PlantUML file.
    """

    def __init__(self):
        """
        Constructor.
        """
        # No name.
        self.name = None
        # No fields
        self.fields = {}

    def parse(self, lines):
        """
        Parse a tables information from the PUML file.
        
        :param lines: The remaining lines of the PUML file. 
        """
        # Use regular expressions to isolate the table name.
        exp = re.search('\s*table\((\w+)', lines[0])
        if exp:
            self.name = exp.group(1)

        # Go through the rest of the lines.
        for line in lines[1:]:
            # Isolate all words and the ending '}'.
            tokens = re.findall(r'[\w\}]+', line)
            # If there was anything to isolate.
            if len(tokens) > 0:
                if tokens[0] == 'primary_key':
                    # This is a prmiare key, add as such.
                    self.fields[tokens[1]] = {'name': tokens[1],
                                              'primary': True,
                                              'type': tokens[2]}
                elif '}' not in line:
                    # This is not a primary key, add it.
                    self.fields[tokens[0]] = {'name': tokens[0],
                                              'primary': False,
                                              'type': tokens[1]}
                else:
                    # Done.
                    break

    def sql(self):
        """
        Return the SQL command to create the table.
        
        :return: SQL command string. 
        """
        # List of foreign keys.
        foreign = ''
        # SQL to create the table itself
        ret = 'CREATE TABLE {}(\n'.format(self.name)

        # Loop over the fields.
        for field in self.fields.values():
            # Add the field.
            ret += ' {0} {1}'.format(field['name'], field['type'])

            if field['primary']:
                # It is a primary key.
                ret += ' PRIMARY KEY'
            ret += ',\n'

            if 'reference' in field.keys():
                # It references another key in another table, add it to the
                # list.
                foreign += ' FOREIGN KEY({0}) REFERENCES {1}({2})'.format(
                    field['name'], field['reference']['table'],
                    field['reference']['field'])
                foreign += ',\n'

        # Add all foreign keys to the end.
        ret += foreign
        return ret[0:-2] + '\n);'


class ForeignKey:
    """
    Parses a foreign key from PlantUML file.
    """

    def __init__(self):
        """
        Constructor.
        """
        # Tables and fields for the foreign key.
        self.source_table = None
        self.source_field = None
        self.target_table = None
        self.target_field = None

    def parse(self, lines):
        """
        Parse a foreign key relatinoship.
        
        :param lines: The remaining lines of the PUML file. 
        """
        # Tokenise by words.
        tokens = re.findall(r'[\w]+', lines[0])
        # Get the direction of the reference.
        dir = re.findall(r'<|>', lines[0])

        # Set the tables and fields according to the direction.
        if (dir[0] == '>'):
            self.source_table = tokens[0]
            self.source_field = tokens[1]
            self.target_table = tokens[3]
            self.target_field = tokens[2]
        elif (dir[0] == '<'):
            self.source_table = tokens[3]
            self.source_field = tokens[2]
            self.target_table = tokens[0]
            self.target_field = tokens[1]
        else:
            print('Error parsng foreign key: {}'.format(lines[0]))


def lineNormalise(line):
    """
    Utillity function convert string to a known format by:
     
     * Stripping any whitespaces at the beginning.
     * Converting to lower case.
    
    :param line: The string to process.
    :return: The processed string.
    """
    # Strip initial whitespaces and lower case the string.
    return (line.lstrip().lower())


def isTable(line):
    """
    Tell if a PlantUML table definition is starting at this line.
    
    :param line: The line to check. 
    :return: True if there is a table definition is starting at this line.
    """
    # Make the string easier to parse.
    line_stripped = lineNormalise(line)

    # Return value.
    ret = False

    # If the line starts with the word table, we have a table definition!
    if line_stripped.startswith('table'):
        ret = True

    # Tell the horrible truth that this code could not find a table.
    return ret


def isForeignKey(line):
    """
    Tell if a PlantUML foreign key definition is at this line.

    :param line: The line to check. 
    :return: True if there is a foreign key definition is at this line.
    """
    # Make the string easier to parse.
    line_stripped = lineNormalise(line)

    # Return value.
    ret = False

    # Split into tokens by space.
    tokens = line.split(' ')

    # Parse the tokens
    for token in tokens:
        # Match direction tokens, these should only appear in foreign key
        # lines.
        if ('<' in token) or ('>' in token):
            ret = True
            # Got it, get out.
            break

    return ret


class PUMLReader:
    """
    Class to read, parse, and convert tables from a PlantUML file into SQL
    commands to create them in the database.
    """
    keywords = (
        '@startuml', 'skinparam', 'scale', '!', 'hide methods',
        'hide stereotypes',
        'sprite', '@enduml')

    def __init__(self):
        """
        Constructor.
        """
        # All tables en up here.
        self.tables = {}

    def parse(self, lines):
        """
        Parse all lines of a PlantUML file.
        
        :param lines: The lines in the PlantUML file.
        """
        # Keep count of the current line number.
        i = 0

        # Array of foreign keys.
        fks = []

        # Loop through all lines.
        for i in range(0, len(lines)):
            # Used to ok parsing of the line.
            skip = False

            # Look for keywords at the beginning of the line.
            for keyword in PUMLReader.keywords:
                if lines[i].startswith(keyword):
                    # Found one, do not parse.
                    skip = True

            # Only parse lines that has no keywords.
            if not skip:
                if isTable(lines[i]):
                    # There was a table at that line, parse it.
                    table = Table()
                    table.parse(lines[i:])
                    # Add it.
                    self.tables[table.name] = table
                elif isForeignKey(lines[i]):
                    # There was a foreign key at that line, parse it.
                    fk = ForeignKey()
                    fk.parse(lines[i:])
                    # Add it
                    fks.append(fk)

        # Add all foreign keys to the tables.
        for name, table in self.tables.items():
            for fk in fks:
                # Find the right table to add the foreign key.
                if fk.source_table == name:
                    table.fields[fk.source_field]['reference'] = {
                        'table': fk.target_table, 'field': fk.target_field}

    def sql(self):
        """
        Return the SQL command to create the tables.

        :return: SQL command string. 
        """
        # Return value.
        ret = ''

        # Variables for figuring out dependencies between tables.
        done = []
        dependencies = {}

        # Run through all tables.
        for table in self.tables.values():
            # Assume no references.
            reference = False

            # Check fields for references.
            for field in table.fields.values():
                if 'reference' in field.keys():
                    # Add the reference to the dependencies of the table.
                    if table.name not in dependencies.keys():
                        dependencies[table.name] = []
                    dependencies[table.name].append(
                        field['reference']['table'])
                    reference = True

            # If the table has no dependencies, just print it.
            if not reference:
                ret += '\n' + table.sql()
                done.append(table.name)

        # Solve dependencies.
        while (len(dependencies) > 0):
            # Run through all dependencies.
            for table, deplist in dependencies.items():
                # Check is some has been solved since the last run.
                for solved in done:
                    if solved in deplist:
                        # Bingo. Remove it.
                        deplist.remove(solved)
                # If there are no more dependencies
                if len(deplist) == 0:
                    # Add thw SQL to the return value,
                    ret += '\n' + self.tables[table].sql()
                    # Add the table name to the solved list.
                    done.append(table)

            # Remove all tables that have had its dependencies solved.
            for solved in done:
                if solved in dependencies.keys():
                    del dependencies[solved]

        return ret


def parse_commandline():
    """
    Parse command line arguments.
    
    :return: Plant UML input file.
    """
    # Set up the arguments.
    parser = ArgumentParser(description='dbdia2sql v{}'.format(__VERSION__) +
                                        ' by Martin B. K. Grønholdt\n Convert' +
                                        ' a Plant UML databse diagram to the ' +
                                        ' SQL statements needed to create the' +
                                        ' datbase.')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='PlantUML file to read the database structure' +
                             ' from.')

    # Parse command line
    args = parser.parse_args()

    # Return the paths.
    return ((args.infile))


def main():
    """
    Program main entry point.
    """
    # Parse the command line.
    puml_file = parse_commandline()

    # Instantiate the PUMLReader class and parse the file given on the command
    # line.
    reader = PUMLReader()
    reader.parse(puml_file.readlines())

    # Print the SQL.
    print(reader.sql())


# Run this when invoked directly
if __name__ == '__main__':
    main()
