#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
"""
Name: table.py
Author: Martin Bo Kristensen Grønholdt.
Since: 2017-08-08

Convert a database table written in a subset of PlantUML to SQLite syntax.
"""
import re
from collections import OrderedDict


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
        self.fields = OrderedDict()

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
            tokens = re.findall(r'[\w\.\}]+', line)
            # If there was anything to isolate.
            if len(tokens) > 0:
                if tokens[0] == 'primary_key':
                    # This is a primary key, add as such.
                    self.fields[tokens[1]] = {'name': tokens[1],
                                              'primary': True,
                                              'foreign': False,
                                              'type': tokens[2]}
                elif tokens[0] == 'foreign_key':
                    # This is a foreign key, add as such.
                    self.fields[tokens[1]] = {'name': tokens[1],
                                              'primary': False,
                                              'foreign': tokens[2],
                                              'type': tokens[3]}
                elif '}' not in line:
                    # This key has no foreign or promary key constrants.
                    self.fields[tokens[0]] = {'name': tokens[0],
                                              'primary': False,
                                              'foreign': False,
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
            ret += '\t{0} {1}'.format(field['name'], field['type'])

            if field['primary']:
                # It is a primary key.
                ret += ' PRIMARY KEY'
            ret += ',\n'

            if field['foreign']:
                # It is a foreign key.
                ret += '\tFOREIGN KEY({0}) REFERENCES {1}({2})'.format(
                    field['name'],
                    field['foreign'].split('.')[0],
                    field['foreign'].split('.')[1])
                ret += ',\n'

        return ret[0:-2] + '\n);'
