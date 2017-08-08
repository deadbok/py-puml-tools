CREATE TABLE productTable(
product TEXT,
idProd INTEGER PRIMARY KEY);

CREATE TABLE countryTable(
idCountry INTEGER PRIMARY KEY,
country TEXT);

CREATE TABLE cityTable(
country TEXT,
city TEXT,
idCity INTEGER PRIMARY KEY,
FOREIGN KEY(country) REFERENCES countryTable(idCountry));

CREATE TABLE customerTable(
address TEXT,
email TEXT,
idCust INTEGER PRIMARY KEY,
name TEXT,
city TEXT,
FOREIGN KEY(city) REFERENCES cityTable(idCity));

CREATE TABLE orderTable(
idOrder INTEGER PRIMARY KEY,
date DATE,
custId INTEGER,
FOREIGN KEY(custId) REFERENCES customerTable(idCust));

CREATE TABLE orderProductTable(
orderId INTEGER PRIMARY KEY,
productId INTEGER,
FOREIGN KEY(orderId) REFERENCES orderTable(idOrder),
FOREIGN KEY(productId) REFERENCES productTable(idProd));