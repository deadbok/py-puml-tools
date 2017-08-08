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
    pass


class SQL2PUML(SQLParseTables):
    puml_template = """
@startuml

skinparam monochrome true
skinparam linetype ortho
scale 2

!define table(x) class x << (T,#FFAAAA) >>
!define view(x) class x << (V,#FFAAAA) >>
!define ent(x) class x << (E,#FFAAAA) >>

!define primary_key(x) <b>PK: x</b>
!define foreign_key(x) <b>FK: </b>x
hide methods
hide stereotypes

{}
@enduml
    """
    puml_tables = OrderedDict()
    # Equals name of the table if processing a table.
    current_table = None

    def add_table(self, name):
        """
        Add the intital setup to the PUML document.
        :return: None
        """
        self.puml_tables[name] = {
            'default': OrderedDict(),
            'foreign': OrderedDict(),
            'primary': OrderedDict()
        }
        self.current_table = name

    def add_column(self, name, type):
        """
        Add column with a simple variable.
        :return: None
        """
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['default'][name] = type


    def add_column_primary(self, name, type):
        """
        Add column with a simple variable.
        :return: None
        """
        """
        Add column with a simple variable.
        :return: None
        """
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['primary'][name] = type

    def add_column_foreign(self, name, type, reference):
        """
        Add column with a simple variable.
        :return: None
        """
        if self.current_table is None:
            raise NoTableException

        self.puml_tables[self.current_table]['foreign'][name] = type

    def clear(self):
        self.puml_tables = OrderedDict()
        self.current_table = None

    def transform(self, sql):
        """
        Transform SQL CREATE TABLE statements to a Plant UML database graph.
        :param sql: SQL file.
        :return: PUML document string.
        """
        self.clear()
        self.parse(sql)
        puml_lines = list()

        for table_name, table in self.puml_tables.items():
            puml_lines.append('table({}) '.format(table_name) + '{')
            for cname, ctype  in table['primary'].items():
                puml_lines.append('\tprimary_key({}) {}'.format(cname, ctype))
            for cname, ctype  in table['foreign'].items():
                puml_lines.append('\tforeign_key({}) {}'.format(cname, ctype))
            if len(table['default'].keys()) > 0:
                puml_lines.append('\t---')
            for cname, ctype  in table['default'].items():
                puml_lines.append('\t{} {}'.format(cname, ctype))
            puml_lines.append('}')
            puml_lines.append('')

        content = '\n'.join(puml_lines)
        return (self.puml_template.format(content))
