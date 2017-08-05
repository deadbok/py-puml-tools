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


class SQLParseTables:
    def parse(self, sql):
        """
        Use sqlparse to parse the SQL file.

        MySQL CREATE TABLE syntax: https://dev.mysql.com/doc/refman/5.7/en/create-table.html

        :param sql: The SQL string to parse.
        :return:
        """
        if not isinstance(sql, str):
            sql = str(sql.read())
        # Isolate CREATE statements.
        for match in re.finditer(r'CREATE\s+TABLE[^;]+;', sql,
                                 re.DOTALL):
            create_stmt = match.group(0)

            # Get the table name.
            match = re.search(r'CREATE\s+TABLE\s+(\[[\w ]+\]|\w+)\s',
                              create_stmt)
            self.add_table(match.group(1).strip('[]'))

            # Isolate defintions
            match = match = re.search(r'\((.*)\)', create_stmt, re.DOTALL)
            definition = match.group(1)
            # Split them into a list by the endning comma.
            definition_list = re.split(r',\s+', match.group(1))
            # List of parsed column definitions.
            columns = list()
            # Parse defintiions.
            columns = list()

            for definition in definition_list:
                column = dict()
                # Clean up the definition.
                definition = definition.replace('\n', '').replace('\t',
                                                                  '').lstrip(
                    ' ')

                # Find names and types.
                match = re.search(r'^(\[[\w ]+\]|\w+)\s+(\w+)\s*(\w*)',
                                  definition)
                # Only process column definitions.
                if match is not None:
                    if match.group(1) not in ['CONSTRAINT',
                                              'INDEX',
                                              'KEY',
                                              'FULLTEXT',
                                              'SPATIAL',
                                              'CHECK',
                                              'FOREIGN']:
                        if match.group(3) == 'PRIMARY':
                            column['name'] = match.group(1).strip('[]')
                            column['type'] = match.group(2)
                            column['primary'] = True
                            column['foreign'] = False
                        else:
                            column['name'] = match.group(1).strip('[]')
                            column['type'] = match.group(2)
                            column['primary'] = False
                            column['foreign'] = False

                        columns.append(column)

                # Find constraints.
                match = re.search(r'^CONSTRAINT\s+(\[[\w ]+\]|\w+)\s+(.*)',
                                  definition)
                if match is not None:
                    # Ignore the (symbol) name of the constraint for now.
                    definition = match.group(2)
                    if definition.startswith('PRIMARY'):
                        var_name_begin = definition.find('(') + 1
                        var_name_end = definition.find(')')
                        name = definition[var_name_begin:var_name_end].strip(
                            '[]')

                        for i in range(0, len(columns)):
                            if columns[i]['name'] == name:
                                columns[i]['primary'] = True
                    if definition.startswith('FOREIGN'):
                        column['primary'] = False
                        column['foreign'] = True
                        definition_tokens = definition.split(' ')
                        print(str(definition_tokens))

                        for token in definition_tokens:
                            if token.startswith('('):
                                column['name'] = token.strip('()[]')

            for column in columns:
                if column['primary']:
                    self.add_column_primary(column['name'], column['type'])
                elif column['foreign']:
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
