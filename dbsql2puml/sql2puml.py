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


class SQL2PUML(SQLParseTables):
    def __init__(self):
        # True if processing a table.
        self.in_table = False
        # PUML output.
        self.puml = '';

    def initialise_puml(self):
        """
        Add the intital setup to the PUML document.
        :return: None
        """
        self.puml = """
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
       """

    def add_table(self, name):
        """
        Add the intital setup to the PUML document.
        :return: None
        """
        # Close the last table.
        if self.in_table:
            self.puml += '\n}\n'

        self.puml += '\nent({}) '.format(name)
        self.puml += '{'
        self.in_table = True

    def add_column_var(self, name, type):
        """
        Add column with a simple variable.
        :return: None
        """
        self.puml += '\n\t{} {}'.format(name, type)

    def end_puml(self):
        """
        Add the PUML document end code.
        :return: None
        """
        # Close the last table.
        if self.in_table:
            self.puml += '\n}\n'

        self.puml += '\n@enduml'

    def transform(self, sql):
        """
        Transform SQL CREATE TABLE statements to a Plant UML database graph.
        :param sql: SQL file.
        :return: PUML document string.
        """
        self.initialise_puml()
        self.parse(sql)
        self.end_puml()
        return (self.puml)
