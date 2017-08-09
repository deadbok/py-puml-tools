# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------

"""
Name: sql2puml..py
Author: Martin Bo Kristensen Grønholdt.

Parse SQL tables into a Plant UML databse diagram.
"""
from sqlparsetables import SQLParseTables
from collections import OrderedDict

class NoTableException(ValueError):
    """
    Exception raised when trying to add a column without first adding a table.
    """
    pass


class SQL2PUML(SQLParseTables):
    """
    Parse SQL and convert CREATE TABLE statements to a Plant UML databse graph.
    """
    # Plant UML database document template.
    puml_template = """
@startuml

skinparam monochrome true
skinparam linetype ortho
scale 2

!define table(x) class x << (T,#FFAAAA) >>
!define view(x) class x << (V,#FFAAAA) >>
!define ent(x) class x << (E,#FFAAAA) >>

!define primary_key(x) <b>PK: x</b>
!define foreign_key(x,reference) <b>FK: </b>x
hide methods
hide stereotypes

{}
@enduml
    """
    # Template structure when the SQL is parsed.
    puml_tables = OrderedDict()
    # Equals name of the table if processing a table.
    current_table = None

    def add_table(self, name):
        """
        Add a table to the PUML structure.

        :param name: Name of the table.
        """
        self.puml_tables[name] = {
            'default': OrderedDict(),
            'foreign': OrderedDict(),
            'primary': OrderedDict()
        }
        # Set current table name.
        self.current_table = name

    def add_column(self, name, type):
        """
        Add a column to a table in the PUML structure.

        :param name: Name of the column.
        :param type: Type of the column.
        """
        # Refuse if not in a table
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['default'][name] = type


    def add_column_primary(self, name, type):
        """
        Add a primary key to a table in the PUML structure.

        :param name: Name of the primary key.
        :param type: Type of the primary key.
        """
        # Refuse if not in a table
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['primary'][name] = type

    def add_column_foreign(self, name, type, reference):
        """
        Add a foreign key to a table in the PUML structure.

        :param name: Name of the foreign key.
        :param type: Type of the foreign key.
        :param reference: Foreign key reference.
        """
        # Refuse if not in a table
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['foreign'][name] = (type, reference)

    def clear(self):
        """
        Clear the variabes used while generating the Plant UML output.
        """
        self.puml_tables = OrderedDict()
        self.current_table = None

    def transform(self, sql):
        """
        Transform SQL CREATE TABLE statements to a Plant UML database graph.

        :param sql: SQL file.
        :return: PUML document string.
        """
        # Start from scratch.
        self.clear()
        # Parse the SQL into the internal structure.
        self.parse(sql)

        # Create an empty list of linus in the output.
        puml_lines = list()
        # Run through all tables.
        for table_name, table in self.puml_tables.items():
            # Add PUML code for the beggining of the table.
            puml_lines.append('table({}) '.format(table_name) + '{')

            # Add PUML lines for all primary keys.
            for cname, ctype  in table['primary'].items():
                puml_lines.append('\tprimary_key({}) {}'.format(cname, ctype))

            # Add PUML lines for all foreign keys.
            for cname, cval  in table['foreign'].items():
                puml_lines.append('\tforeign_key({},{}) {}'.format(cname, cval[1], cval[0]))

            # Add separator if there is regular columns.
            if len(table['default'].keys()) > 0:
                puml_lines.append('\t---')

            # Add regular columns.
            for cname, ctype  in table['default'].items():
                puml_lines.append('\t{} {}'.format(cname, ctype))

            # Close the table.
            puml_lines.append('}')
            # Add a single empty line.
            puml_lines.append('')

        # Run through all foreign keys and crete the table relations.
        for table_name, table in self.puml_tables.items():
            for fk  in table['foreign'].values():
                puml_lines.append('{} "0..n" -- "1..1" {}'.format(table_name, fk[1].split('.')[0]))

        # Add a single empty line.
        puml_lines.append('')

        # Join all output lines separated by new lines.
        content = '\n'.join(puml_lines)

        # Return the final PUML string.
        return (self.puml_template.format(content))
