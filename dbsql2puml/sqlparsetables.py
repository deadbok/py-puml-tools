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
import sqlite3
import tempfile


class SQLParseTables:
    tables = OrderedDict()
    db = None
    cursor = None

    def parse(self, sql):
        """
        Use sqlparse to parse the SQL file.

        MySQL CREATE TABLE syntax: https://dev.mysql.com/doc/refman/5.7/en/create-table.html

        :param sql: The SQL string to parse.
        :return:
        """
        db_file = tempfile.NamedTemporaryFile('w')
        self.db = sqlite3.connect(db_file.name)
        self.db.execute('pragma foreign_keys=ON')
        self.cursor = self.db.cursor()

        # If 'sql' is not a string assume it is a file.
        if not isinstance(sql, str):
            sql = str(sql.read())

        self.cursor.executescript(sql)
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        self.tables = OrderedDict()
        for table in tables:
            self.tables[table[0]] = OrderedDict()
            self.cursor.execute('PRAGMA table_info({})'.format(table[0]))

            for sql_column in self.cursor.fetchall():
                column = dict()
                column['name'] = sql_column[1]
                column['type'] = sql_column[2]
                column['primary'] = False
                if sql_column[5] == 1:
                    column['primary'] = True
                column['foreign'] = False

                self.tables[table[0]][sql_column[1]] = column

            self.cursor.execute('PRAGMA foreign_key_list({});'.format(table[0]))
            for foreign_key in self.cursor.fetchall():
                src_column = foreign_key[3]
                for name, column in self.tables[table[0]].items():
                    if name == src_column:
                        self.tables[table[0]][name]['foreign'] = '{}.{}'.format(foreign_key[2], foreign_key[4])

        self.db.close()
        self.cursor = None

        for table_name, columns in self.tables.items():
            self.add_table(table_name)

            for column in columns.values():
                if column['primary'] is True:
                    self.add_column_primary(column['name'], column['type'])
                if column['foreign'] is not False:
                    self.add_column_foreign(column['name'], column['type'], column['foreign'])
                if ((column['primary'] is not True) and
                        (column['foreign'] is False)):
                    self.add_column(column['name'], column['type'])

    def add_table(self, name):
        raise NotImplementedError(
            "Please implement the 'add_table' method in a derived class.")

    def add_column(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")

    def add_column_primary(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column_primary' method in a derived class.")

    def add_column_foreign(self, name, type, reference):
        raise NotImplementedError(
            "Please implement the 'add_column_foreign' method in a derived class.")

