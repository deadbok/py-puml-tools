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

*This parser rely on sqlite, but has not been tested very much and is probably
easy to fool.*
"""
import re
from collections import OrderedDict
import sqlite3
import tempfile


class SQLParseTables:
    """
    Parse SQL CREATE statements for column definitions, PRIMARY KEYs, and FOREIGN KEYs.
    """
    tables = OrderedDict()
    db = None
    cursor = None

    def parse(self, sql):
        """
        Use sqlite to parse the SQL file.

        MySQL CREATE TABLE syntax: https://dev.mysql.com/doc/refman/5.7/en/create-table.html

        :param sql: The SQL string to parse.
        """
        # Get a temporary file name for sqlite
        db_file = tempfile.NamedTemporaryFile('w')
        # Connect to the temporary file.
        self.db = sqlite3.connect(db_file.name)
        # Enable foreign keys.
        self.db.execute('pragma foreign_keys=ON')
        # Get a cursor instance.
        self.cursor = self.db.cursor()

        # If sql is not a string assume it is a file.
        if not isinstance(sql, str):
            # Read the file into sql.
            sql = str(sql.read())

        # Execute the SQL statements from the input.
        self.cursor.executescript(sql)

        # Get all table names.
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        # Initialise the variable containing the parsed tables.
        self.tables = OrderedDict()
        # Run through all tables.
        for table in tables:
            # Create an entry for each table.
            self.tables[table[0]] = OrderedDict()

            # Get info on columns and primary keys.
            self.cursor.execute('PRAGMA table_info({})'.format(table[0]))
            # For each column
            for sql_column in self.cursor.fetchall():
                # Create an empty column entry.
                column = dict()
                # Set the name.
                column['name'] = sql_column[1]
                # Set the type
                column['type'] = sql_column[2]
                # Determine if this is a primary key
                column['primary'] = False
                if sql_column[5] == 1:
                    column['primary'] = True
                # We do not know if this key has a reference yet.
                column['foreign'] = False

                # Add the column to the table.
                self.tables[table[0]][sql_column[1]] = column

            # Get information on foreign keys.
            self.cursor.execute('PRAGMA foreign_key_list({});'.format(table[0]))
            # Run through all foreign keys
            for foreign_key in self.cursor.fetchall():
                # Find the column by its name.
                for name, column in self.tables[table[0]].items():
                    # Search for the name of the source column.
                    if name == foreign_key[3]:
                        # Add the referenced table and column in dot notation.
                        self.tables[table[0]][name]['foreign'] = '{}.{}'.format(foreign_key[2], foreign_key[4])

        # Close the database connection
        self.db.close()
        # Make the cursor unusable for good measure.
        self.cursor = None

        # Run through the parsed tables and dispatch to the related call backs.
        for table_name, columns in self.tables.items():
            # New table.
            self.add_table(table_name)

            # Table columns.
            for column in columns.values():
                # Primary key.
                if column['primary'] is True:
                    self.add_column_primary(column['name'], column['type'])
                # Foreign key.
                if column['foreign'] is not False:
                    self.add_column_foreign(column['name'], column['type'], column['foreign'])
                # Just a column.
                if ((column['primary'] is not True) and
                        (column['foreign'] is False)):
                    self.add_column(column['name'], column['type'])

    def add_table(self, name):
        """
        Implement this to catch new tables"

        :param name: Name of the table.
        """
        raise NotImplementedError(
            "Please implement the 'add_table' method in a derived class.")

    def add_column(self, name, type):
        """
        Implement this to catch new columns"

        :param name: Name of the column.
        :param type: Type of the column.
        """
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")

    def add_column_primary(self, name, type):
        """
        Implement this to catch new primary keys"

        :param name: Name of the primary key.
        :param type: Type of the primary key.
        """
        raise NotImplementedError(
            "Please implement the 'add_column_primary' method in a derived class.")

    def add_column_foreign(self, name, type, reference):
        """
        Implement this to catch new primary keys"

        :param name: Name of the primary key.
        :param type: Type of the primary key.
        :param reference: Foreign key reference.
        """
        raise NotImplementedError(
            "Please implement the 'add_column_foreign' method in a derived class.")
