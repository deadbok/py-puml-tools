#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
"""
Name: pumlreader.py
Author: Martin Bo Kristensen Grønholdt.
Since: 2017-08-08

Convert a database diagram written in a subset of PlantUML to SQLite syntax.
"""
from table import Table


def lineNormalise(line):
    """
    Utility function to convert string to a known format by:

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

            # Check fields for foreign keys.
            for field in table.fields.values():
                if field['foreign'] is not False:
                    # Add the reference to the dependencies of the table.
                    if table.name not in dependencies.keys():
                        dependencies[table.name] = []
                    dependencies[table.name].append(
                        field['foreign'].split('.')[0])
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