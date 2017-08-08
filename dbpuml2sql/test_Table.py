from unittest import TestCase

from table import Table

from collections import OrderedDict


class TestTable(TestCase, Table):
    def setUp(self):
        Table.__init__(self)

    def test_parse(self):
        """Testing table parser"""
        self.maxDiff = None
        puml = """
table(customerTable) {
\tprimary_key(idCust) INTEGER
\tforeign_key(city, cityTable.idCity) TEXT
\t---
\taddress TEXT
\temail TEXT
\tname TEXT
}
""".strip().split('\n')

        fields = {
            'idCust': {
                'name': 'idCust',
                'primary': True,
                'foreign': False,
                'type': 'INTEGER'
            },
            'city': {
                'name': 'city',
                'primary': False,
                'foreign': 'cityTable.idCity',
                'type': 'TEXT'
            },
            'address': {
                'name': 'address',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            },
            'email': {
                'name': 'email',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            },
            'name': {
                'name': 'name',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            }
        }
        self.parse(puml)
        self.assertEqual(self.name, 'customerTable')
        self.assertDictEqual(self.fields, fields)

    def test_sql(self):
        """Testing table SQL writer"""
        self.maxDiff = None
        sql = """
CREATE TABLE customerTable(
\tidCust INTEGER PRIMARY KEY,
\tcity TEXT,
\tFOREIGN KEY(city) REFERENCES cityTable(idCity),
\taddress TEXT,
\temail TEXT,
\tname TEXT
);
""".strip()
        self.name = 'customerTable'
        self.fields = OrderedDict()
        self.fields['idCust'] = {
                'name': 'idCust',
                'primary': True,
                'foreign': False,
                'type': 'INTEGER'
            }
        self.fields['city'] = {
                'name': 'city',
                'primary': False,
                'foreign': 'cityTable.idCity',
                'type': 'TEXT'
            }
        self.fields['address'] = {
                'name': 'address',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            }
        self.fields['email'] = {
                'name': 'email',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            }
        self.fields['name'] = {
                'name': 'name',
                'primary': False,
                'foreign': False,
                'type': 'TEXT'
            }
        self.assertEqual(self.sql(), sql)
