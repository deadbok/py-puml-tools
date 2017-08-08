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
import sqlite3

class SQLTestBase(SQLParseTables, unittest.TestCase):
    subtest = 0
    results = False
    current_table = None
    tables_struct = dict()

    def add_table(self, name):
        """
        Test adding of tables. This is implemented in the base, as all test
        create new tables.

        :param name: Name of the new table.
        """
        self.results = True
        table_names = self.tables_struct.keys()
        if self.subtest != 0:
            with self.subTest('Test {}'.format(str(self.subtest))):
                self.assertIn(name, table_names)
                self.current_table = name
        else:
            self.assertIn(name, self.table_names)

    def add_column(self, name, type):
        self.results = True
        if self.subtest != 0:
            with self.subTest('Test {}'.format(str(self.subtest))):
                self.fail('Called add_column')
        else:
            self.fail('Called add_column')

    def add_column_primary(self, name, type):
        self.results = True
        if self.subtest != 0:
            with self.subTest('Test {}'.format(str(self.subtest))):
                self.fail('Called add_column_primary')
        else:
            self.fail('Called add_column_primary')

    def add_column_foreign(self, name, type, reference):
        self.results = True
        if self.subtest != 0:
            with self.subTest('Test {}'.format(str(self.subtest))):
                self.fail('Called add_column_foreign')
        else:
            self.fail('Called add_column_foreign')

    def tearDown(self):
        self.assertTrue(self.results, 'No results from parser.')


class SQLParseTableTest(SQLTestBase):
    """CREATE TABLE"""
    tables_struct = {
        'Test': {
            'col': ('INTVAR', False, False)
        }
    }

    def test_table(self):
        """Test simple CREATE TABLE statements"""
        self.subtest += 1
        sql = 'CREATE TABLE {} ( {} {} {});'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '')
        self.parse(sql)

        self.subtest += 1
        sql = 'CREATE TABLE [{}] ( [{}] [{}] [{}]);'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '')
        self.parse(sql)

    def add_column(self, name, type):
        self.results = True
        with self.subTest('Test {}'.format(str(self.subtest))):
            self.assertNotEqual(self.current_table, None,
                                'Trying to instert column with no active table.')
            column_names = [col_name for col_name in
                            self.tables_struct[self.current_table].keys()]
            self.assertIn(name, column_names)
            self.assertEqual(type,
                             self.tables_struct[self.current_table][name][0])

    def tearDown(self):
        self.assertTrue(self.results, 'No results from parser.')


class SQLParsePrimaryKeyTest(SQLTestBase):
    """PRIMARY KEY"""
    tables_struct = {
        'Test': {
            'col': ('INTVAR', True, False)
        }
    }

    def test_table1(self):
        """Test PRIMARY KEY at column definition"""
        self.subtest += 1
        sql = 'CREATE TABLE {} ( {} {} {});'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '')
        self.parse(sql)

        self.subtest += 1
        sql = 'CREATE TABLE [{}] ( [{}] [{}] {});'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '')
        self.parse(sql)

    def test_table2(self):
        """Test PRIMARY KEY as CONSTRAINT statement"""
        self.subtest += 1
        sql = 'CREATE TABLE {} ( {} {}, CONSTRAINT pk_test PRIMARY KEY({}));'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'col')
        self.parse(sql)

        self.subtest += 1
        sql = 'CREATE TABLE [{}] ( [{}] [{}], CONSTRAINT pk_test PRIMARY KEY({}));'.format(
            'Test',
            'col',
            self.tables_struct['Test']['col'][0],
            'col')
        self.parse(sql)

    def add_column_primary(self, name, type):
        self.results = True
        with self.subTest('Test {}'.format(str(self.subtest))):
            self.assertNotEqual(self.current_table, None,
                                'Trying to instert column with no active table.')
            column_names = [col_name for col_name in
                            self.tables_struct[self.current_table].keys()]
            self.assertIn(name, column_names)
            self.assertEqual(type,
                             self.tables_struct[self.current_table][name][0])

    def tearDown(self):
        self.assertTrue(self.results, 'No results from parser.')


class SQLParseForeignKeyTest(SQLTestBase):
    """FOREIGN KEY"""
    foreign = False
    tables_struct = {
        'Test': {
            'col': ('INTVAR', True, 'other(col)')
        },
        'other': {
            'col': ('INTVAR', True, False)
        }
    }

    def test_table(self):
        """Test CONSTRAINT FOREIGN KEY"""
        self.subtest += 1
        sql = """
CREATE TABLE {} ( {} {} {});
CREATE TABLE {} ( {} {} {}, CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} );
""".format('other',
           'col',
           self.tables_struct['other']['col'][0],
           'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '',
           'Test',
           'col',
           self.tables_struct['Test']['col'][0],
           'PRIMARY KEY' if self.tables_struct['Test']['col'][1] else '',
           'fk_test',
           'col',
           self.tables_struct['Test']['col'][2])

        self.parse(sql)

    def add_column_primary(self, name, type):
        self.results = True
        with self.subTest('Test {}'.format(str(self.subtest))):
            self.assertNotEqual(self.current_table, None,
                                'Trying to insert column with no active table.')
            column_names = [col_name for col_name in
                            self.tables_struct[self.current_table].keys()]
            self.assertIn(name, column_names)
            self.assertEqual(type,
                             self.tables_struct[self.current_table][name][0])

    def add_column_foreign(self, name, type, reference):
        self.results = True
        self.foreign = True
        with self.subTest('Test {}'.format(str(self.subtest))):
            self.assertNotEqual(self.current_table, None,
                                'Trying to insert column with no active table.')
            column_names = [col_name for col_name in
                            self.tables_struct[self.current_table].keys()]
            self.assertIn(name, column_names)
            self.assertEqual(type,
                             self.tables_struct[self.current_table][name][0])
            self.assertEqual(reference,
                             'other.col')

    def tearDown(self):
        self.assertTrue(self.foreign, 'No foreign keys added.')
        SQLTestBase.tearDown(self)

class SQLParseWrongInputTest(SQLTestBase):
    def test_table(self):
        """Test malformed SQL input"""
        self.subtest += 1
        sql = 'dlkjeoi lkdlnj'

        with self.assertRaises(sqlite3.OperationalError):
            self.parse(sql)

    def tearDown(self):
        pass



if __name__ == '__main__':
    unittest.main()
