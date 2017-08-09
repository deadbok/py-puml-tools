#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
# Program to convert a database diagram written in a subset of PlantUML to
# SQLite syntax that will create the actual tables and relations.
#
# Version 0.9.0 (2017-08-09)
#  * Update Plant UML syntax for foreign keys.
#
# Version 0.8.0 (2017-08-08)
#  * Add README.
#
# Version 0.7.0 (2017-08-08)
#  * Add comments
#
# Version 0.6.0 (2017-08-08)
#  * Add relation to PUML output.
#
# Version 0.5.0 (2017-08-08)
#  * Add parsing of SQL.
#  * Conversion of tables into Plant UML format.
#  * Rendering of Plant UML database graph template.
#
# Version 0.0.1 (2017-08-03)
#  * Skeleton
#

"""
Name: dbsql2puml.py
Author: Martin Bo Kristensen Grønholdt.
Version: 0.8.0

Convert SQL file to a Plant UML database diagram.
"""
from argparse import ArgumentParser
import argparse
from sql2puml import SQL2PUML

# Program version.
__VERSION__ = '0.8.0'


def parse_commandline():
    """
    Parse command line arguments.
    
    :return: Input SQL file.
    """
    # Set up the arguments.
    parser = ArgumentParser(description='dbsql2puml v{}'.format(__VERSION__) +
                                        ' by Martin B. K. Grønholdt\n Convert' +
                                        ' a SQL file to a Plant UML Diagram')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='SQL file with CREATE statements.')

    # Parse command line
    args = parser.parse_args()

    # Return the paths.
    return (args.infile)


def main():
    """
    Program main entry point.
    """
    # Parse the command line.
    sql_file = parse_commandline()

    # Create an instance of the converter class.
    puml = SQL2PUML()
    # Call it with the file and print the result.
    print(puml.transform(sql_file))


# Run this when invoked directly
if __name__ == '__main__':
    main()
