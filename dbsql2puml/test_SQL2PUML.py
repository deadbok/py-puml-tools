from unittest import TestCase
from collections import OrderedDict

from sql2puml import SQL2PUML
from sql2puml import NoTableException


class TestSQL2PUML(TestCase, SQL2PUML):
    def test_add_table(self):
        self.clear()
        self.add_table('Test')
        self.assertIn('Test', self.puml_tables)

    def test_add_column(self):
        self.clear()

        with self.assertRaises(NoTableException):
            self.add_column('col', 'INTVAR')

        self.add_table('Test')
        self.add_column('col', 'INTVAR')
        self.assertIn('col', self.puml_tables['Test']['default'])
        self.assertEqual('INTVAR', self.puml_tables['Test']['default']['col'])

    def test_add_column_primary(self):
        self.clear()

        with self.assertRaises(NoTableException):
            self.add_column_primary('col', 'INTVAR')

        self.add_table('Test')
        self.add_column_primary('col', 'INTVAR')
        self.assertIn('col', self.puml_tables['Test']['primary'])
        self.assertEqual('INTVAR', self.puml_tables['Test']['primary']['col'])

    def test_add_column_foreign(self):
        self.clear()

        with self.assertRaises(NoTableException):
            self.add_column_foreign('col', 'INTVAR', 'other.col')

        self.add_table('Test')
        self.add_column_foreign('col', 'INTVAR', 'other.col')
        self.assertIn('col', self.puml_tables['Test']['foreign'])
        self.assertEqual(('INTVAR', 'other.col'), self.puml_tables['Test']['foreign']['col'])

    def test_clear(self):
        self.clear()
        self.assertEqual(self.puml_tables, OrderedDict())
        self.assertIsNone(self.current_table)

    def test_transform(self):
        self.maxDiff = None
        sql = """
CREATE TABLE productTable(
  product TEXT,
  idProd INTEGER PRIMARY KEY
);

CREATE TABLE countryTable(
  idCountry INTEGER PRIMARY KEY,
  country TEXT
);

CREATE TABLE cityTable(
  country TEXT,
  city TEXT,
  idCity INTEGER PRIMARY KEY,
  FOREIGN KEY(country) REFERENCES countryTable(idCountry)
);

CREATE TABLE customerTable(
    address TEXT,
    email TEXT,
    idCust INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT,
    FOREIGN KEY(city) REFERENCES cityTable(idCity)
);

CREATE TABLE orderTable(
    idOrder INTEGER PRIMARY KEY,
    date DATE,
    custId INTEGER,
    FOREIGN KEY(custId) REFERENCES customerTable(idCust)
);

CREATE TABLE orderProductTable(
    orderId INTEGER PRIMARY KEY,
    productId INTEGER,
    FOREIGN KEY(orderId) REFERENCES orderTable(idOrder),
    FOREIGN KEY(productId) REFERENCES productTable(idProd)
);
"""
        result = """
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

table(productTable) {
\tprimary_key(idProd) INTEGER
\t---
\tproduct TEXT
}

table(countryTable) {
\tprimary_key(idCountry) INTEGER
\t---
\tcountry TEXT
}

table(cityTable) {
\tprimary_key(idCity) INTEGER
\tforeign_key(country,countryTable.idCountry) TEXT
\t---
\tcity TEXT
}

table(customerTable) {
\tprimary_key(idCust) INTEGER
\tforeign_key(city,cityTable.idCity) TEXT
\t---
\taddress TEXT
\temail TEXT
\tname TEXT
}

table(orderTable) {
\tprimary_key(idOrder) INTEGER
\tforeign_key(custId,customerTable.idCust) INTEGER
\t---
\tdate DATE
}

table(orderProductTable) {
\tprimary_key(orderId) INTEGER
\tforeign_key(orderId,orderTable.idOrder) INTEGER
\tforeign_key(productId,productTable.idProd) INTEGER
}

cityTable "0..n" -- "1..1" countryTable
customerTable "0..n" -- "1..1" cityTable
orderTable "0..n" -- "1..1" customerTable
orderProductTable "0..n" -- "1..1" orderTable
orderProductTable "0..n" -- "1..1" productTable

@enduml
""".strip()
        self.assertEqual(result, self.transform(sql).strip(),
                         'PUML document code is incorrect')
