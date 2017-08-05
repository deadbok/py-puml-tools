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

Transform SQL into PUML.
"""
import re


class SQLParseTables:
    def parse(self, sql):
        """
        Use sqlparse to parse the SQL file.

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
            for definition in definition_list:
                # Clean up the definition.
                definition = definition.replace('\n', '').replace('\t',
                                                                  '').lstrip(
                    ' ')

                # Find names and types.
                match = re.search(r'^(\[[\w ]+\]|\w+)\s+(\w+)',
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
                        self.add_column_var(match.group(1).strip('[]'),
                                        match.group(2))

                # Find constraints.
                match = re.search(r'^CONSTRAINT\s+(\[[\w ]+\]|\w+)\s+(.*)',
                                  definition)
                if match is not None:
                    print(match.group(1).strip('[]'))
                    definition = match.group(2)


    def add_table(self, name):
        raise NotImplementedError(
            "Please implement the 'add_table' method in a derived class.")

    def add_column_var(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")

    def add_column_primary(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")

    def add_column_foreign(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")
