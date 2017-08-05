# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------

"""
Name: sqltest..py
Author: Martin Bo Kristensen Grønholdt.

Test SQLParseTable class.
"""
from sqlparsetables import SQLParseTables
import unittest


class SQLParseTableTest(SQLParseTables, unittest.TestCase):
    """CREATE TABLE"""
    table_name = 'Test'
    var_name = 'col'
    var_type = 'INTVAR'

    def test_table(self):
        """Test simple CREATE TABLE statements"""
        self.parse(
            'CREATE TABLE {} ( {} {} );'.format(self.table_name, self.var_name,
                                                self.var_type))
        self.parse(
            'CREATE TABLE [{}] ( {} {} );'.format(self.table_name,
                                                  self.var_name,
                                                  self.var_type))
        self.parse(
            'CREATE TABLE {} ( [{}] {}] );'.format(self.table_name,
                                                   self.var_name,
                                                   self.var_type))
        self.parse(
            'CREATE TABLE [{}] ( [{}] {}] );'.format(self.table_name,
                                                     self.var_name,
                                                     self.var_type))

    def add_table(self, name):
        self.assertEqual(name, self.table_name)

    def add_column(self, name, type):
        self.assertEqual(name, self.var_name)
        self.assertEqual(type, self.var_type)

    def add_column_primary(self, name, type):
        self.fail('Called add_column_primary')

    def add_column_foreign(self, name, type):
        self.fail('Called add_column_foreign')


class SQLParsePrimaryKeyTest(SQLParseTables, unittest.TestCase):
    """PRIMARY KEY"""
    table_name = 'Test'
    var_name = 'col'
    var_type = 'INTVAR'
    pk_name = 'PK_col'

    def test_table1(self):
        """Test PRIMARY KEY at column definition"""
        self.parse(
            'CREATE TABLE {} ( {} {} PRIMARY KEY );'.format(self.table_name,
                                                            self.var_name,
                                                            self.var_type))
        self.parse(
            'CREATE TABLE [{}] ( {} {} PRIMARY KEY );'.format(self.table_name,
                                                              self.var_name,
                                                              self.var_type))
        self.parse(
            'CREATE TABLE {} ( [{}] {} PRIMARY KEY );'.format(self.table_name,
                                                              self.var_name,
                                                              self.var_type))
        self.parse(
            'CREATE TABLE [{}] ( [{}] {} PRIMARY KEY );'.format(
                self.table_name,
                self.var_name, self.var_type))

    def test_table2(self):
        """Test PRIMARY KEY as CONSTRAINT statement"""
        self.parse(
            'CREATE TABLE {} ( {} {}, CONSTRAINT {} PRIMARY KEY({}) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))
        self.parse(
            'CREATE TABLE [{}] ( {} {}, CONSTRAINT {} PRIMARY KEY({}) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))
        self.parse(
            'CREATE TABLE {} ( [{}] {}, CONSTRAINT {} PRIMARY KEY({}) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))
        self.parse(
            'CREATE TABLE {} ( {} {}, CONSTRAINT [{}] PRIMARY KEY({}) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))
        self.parse(
            'CREATE TABLE {} ( {} {}, CONSTRAINT {} PRIMARY KEY([{}]) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))
        self.parse(
            'CREATE TABLE [{}] ( [{}] {}, CONSTRAINT [{}] PRIMARY KEY([{}]) );'.format(
                self.table_name,
                self.var_name, self.var_type, self.pk_name, self.var_name))

    def add_table(self, name):
        self.assertEqual(name, self.table_name)

    def add_column(self, name, type):
        self.fail('Called add_column')

    def add_column_primary(self, name, type):
        self.assertEqual(name, self.var_name)
        self.assertEqual(type, self.var_type)

    def add_column_foreign(self, name, type):
        self.fail('Called add_column_foreign')


class SQLParseForeignKeyTest(SQLParseTables, unittest.TestCase):
    """FOREIGN KEY

    [CONSTRAINT [symbol]] FOREIGN KEY
    [index_name] (index_col_name, ...)
    REFERENCES tbl_name (index_col_name,...)
    [ON DELETE reference_option]
    [ON UPDATE reference_option]

reference_option:
    RESTRICT | CASCADE | SET NULL | NO ACTION | SET DEFAULT"""
    table_name = 'Test'
    var_name = 'col'
    var_type = 'INTVAR'
    con_name = 'CS_col'
    fk_name = 'FK_col'
    ref = 'other.col'

    def test_table(self):
        """Test CONSTRAINT FOREIGN KEY"""
        self.parse(
            'CREATE TABLE {} ( {} {}, CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {});'.format(
                self.table_name,
                self.var_name, self.var_type, self.con_name, self.fk_name,
                self.ref))

    def add_table(self, name):
        self.assertEqual(name, self.table_name)

    def add_column(self, name, type):
        self.fail('Called add_column')

    def add_column_primary(self, name, type):
        self.fail('Called add_column_primary')

    def add_column_foreign(self, name, type):
        self.fail('Called add_column_foreign')


if __name__ == '__main__':
    unittest.main()
