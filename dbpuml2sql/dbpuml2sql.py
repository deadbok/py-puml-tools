#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
#
# Version 1.1.0 (2017-08-08)
#  * Update Plant UML syntax, especially foreign keys.
#
# Version 1.0.2 (2017-08-03)
#  * Fix help description.
#
# Version 1.0.1
#  * Few touch ups
#
# Version 1.0.0
#  * First working version.
#
"""
Name: dbpuml2sql.py
Author: Martin Bo Kristensen Grønholdt.
Version 1.1.0

Convert a database diagram written in a subset of PlantUML to SQLite syntax
that will create the actual tables and relations.
"""
from argparse import ArgumentParser
import argparse
from pumlreader import PUMLReader

# Program version.
__VERSION__ = '1.1.0'


def parse_commandline():
    """
    Parse command line arguments.
    
    :return: Plant UML input file.
    """
    # Set up the arguments.
    parser = ArgumentParser(description='dbpuml2sql v{}'.format(__VERSION__) +
                                        ' by Martin B. K. Grønholdt\n Convert' +
                                        ' a Plant UML databse diagram to the ' +
                                        ' SQL statements needed to create the' +
                                        ' datbase.')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='PlantUML file to read the database structure' +
                             ' from.')

    # Parse command line
    args = parser.parse_args()

    # Return the paths.
    return ((args.infile))


def main():
    """
    Program main entry point.
    """
    # Parse the command line.
    puml_file = parse_commandline()

    # Instantiate the PUMLReader class and parse the file given on the command
    # line.
    reader = PUMLReader()
    reader.parse(puml_file.readlines())

    # Print the SQL.
    print(reader.sql())


# Run this when invoked directly
if __name__ == '__main__':
    main()
