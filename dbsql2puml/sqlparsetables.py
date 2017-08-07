# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------

"""
Name: sqlparsetables.py
Author: Martin Bo Kristensen Grønholdt.

Parse SQL CREATE TABLE statements.

*This parser is not complete, it s tested with some generic statements, but I
am sure it will fall appart given the right input.*
"""
import re
from collections import OrderedDict


class SQLParseTables:
    tables = OrderedDict()
    columns = OrderedDict()

    def get_tables(self, sql):
        """
        Find and return all CREATE TABLE statements.

        :param sql: String of SQL statements.
        :return: Dictionary of table names and table definitions.
        """
        # Isolate CREATE statements.
        for match in re.finditer(r'^CREATE\s+TABLE([^\(]+)\s+\(([^\;]+);', sql,
                                 re.DOTALL):
            name = match.group(1).strip()

            name_begin = name.find('[')
            if name_begin > -1:
                name_end = name.find(']')
                name = name[name_begin + 1:name_end]
            else:
                tokens = name.split(' ')
                name = tokens[-1]

            self.tables[name] = match.group(2)[:-1]

        return (self.tables)

    def parse_definition(self, definition):
        keywords = ['CONSTRAINT', 'INDEX', 'KEY', 'FULLTEXT', 'SPATIAL',
                    'CHECK', 'FOREIGN', 'PRIMARY']

        # Initial column values.
        column = {'name': '', 'type': '', 'primary': False, 'foreign': False}
        tokens = definition.split(' ')

        if tokens[0] not in keywords:
            print(str(tokens))
            column['name'] = tokens[0].strip('[]')
            del tokens[0]
            column['type'] = tokens[0].strip('[]')
            del tokens[0]

            if len(tokens) > 0:
                if tokens[0] == 'PRIMARY':
                    column['primary'] = True

            self.columns[column['name']] = column
        else:
            while len(tokens) > 0:
                if tokens[0] == 'CONSTRAINT':
                    del tokens[0]

                    if tokens[0].startswith('['):
                        while not tokens[0].endswith(']'):
                            del tokens[0]
                        
                    column['name'] = tokens[1].strip('[]')
                    if tokens[2] == 'PRIMARY':
                        column['primary'] = True



                del tokens[0]

            self.columns[column['name']] = column

        return (column)

    def parse(self, sql):
        """
    Use sqlparse to parse the SQL file.

    MySQL CREATE TABLE syntax: https://dev.mysql.com/doc/refman/5.7/en/create-table.html

    :param sql: The SQL string to parse.
    :return:
    """
        if not isinstance(sql, str):
            sql = str(sql.read())

        for name, definitions in self.get_tables(sql).items():
            self.add_table(name)

            # Split them into a list by the endning comma.
            definition_list = re.split(r',\s+', definitions)

            self.columns = OrderedDict()
            for definition in definition_list:
                definition = definition.strip().rstrip()
                self.parse_definition(definition)

        for column in self.columns.values():
            if column['primary'] is True:
                self.add_column_primary(column['name'], column['type'])
            elif column['foreign'] is True:
                self.add_column_foreign(column['name'], column['type'])
            else:
                self.add_column(column['name'], column['type'])

    def add_table(self, name):
        raise NotImplementedError(
            "Please implement the 'add_table' method in a derived class.")

    def add_colum(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")

    def add_column_primary(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column_primary' method in a derived class.")

    def add_column_foreign(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column_foreign' method in a derived class.")
