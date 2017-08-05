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
from ..sqlparsetables import SQLParseTables
import unittest


class SQLParseTableTest(SQLParseTables, unittest.TestCase):
    def setUp(self):
        print(self._testMethodDoc)

    def test_table1(self):
        """Test with: 'CREATE TABLE Test ( col INTVAR );'"""
        self.parse('CREATE TABLE Test ( col INTVAR );')

    def test_table2(self):
        """Test with: 'CREATE TABLE [Test] ( col INTVAR );'"""
        self.parse('CREATE TABLE [Test] ( col INTVAR );')

    def test_table3(self):
        """Test with: 'CREATE TABLE [Test] ( col [INTVAR] );'"""
        self.parse('CREATE TABLE [Test] ( col [INTVAR] );')

    def add_table(self, name):
        self.assertTrue(name, 'Test')

    def add_column_var(self, name, type):
        self.assertTrue(name, 'col')
        self.assertTrue(type, 'INTVAR')

class SQLParsePrimaryKeyTest(SQLParseTables, unittest.TestCase):
    def setUp(self):
        print(self._testMethodDoc)

    def test_table1(self):
        """Test with: 'CREATE TABLE Test ( col INTVAR PRIMARY KEY );'"""
        self.parse('CREATE TABLE Test ( col INTVAR PRIMARY KEY );')

    def test_table2(self):
        """Test with: 'CREATE TABLE [Test] ( col INTVAR, CONSTRAINT [PK_col] PRIMARY KEY([col]) );'"""
        self.parse('CREATE TABLE [Test] ( col INTVAR, CONSTRAINT [PK_col] PRIMARY KEY([col]) );')


    def add_table(self, name):
        self.assertTrue(name, 'Test')

    def add_column_var(self, name, type):
        self.assertTrue(name, 'col')
        self.assertTrue(type, 'INTVAR')

    def add_column_primary(self, name, type):
        raise NotImplementedError(
            "Please implement the 'add_column' method in a derived class.")


if __name__ == '__main__':
    unittest.main()