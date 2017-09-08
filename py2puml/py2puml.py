#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):

# <martin.groenholdt@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Martin B. K. Grønholdt
# --------------------------------------------------------------------------------
"""
Program to parse Python classes and write their info to PlantUML files
(see http://plantuml.com/) that can be used to generate UML files and GraphViz
renderings of classes.

Missing:
 * Inheritance parsing
"""
# pylint: disable=C0103

# standard lib imports
import configparser
import logging
import logging.config
import os
import sys

# other imports
import yaml

# this project imports
from version import __version__
from puml_generator import PUML_Generator, PUML_Generator_NS

HOME_DIR = os.path.dirname(__file__)

# puml indentation unit
TAB = '  '

# list of possible configuration files,
# all existing will be loaded unless a specific config arg is provided
CONFIG_FILENAMES = (
    os.path.join(HOME_DIR, 'py2puml.ini'),
    os.path.expanduser('~/.config/py2puml.ini'),
    os.path.expanduser('~/.py2puml.ini'),
    '.py2puml.ini',
    'py2puml.ini',
)
LOGGING_CFG = os.path.join(HOME_DIR, 'logging.yaml')

with open(LOGGING_CFG) as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger() # (__name__)

def cli_parser():
    "Builds a command line parser suitable for this tool."
    import argparse

    # Takes a python file as a parameter.
    parser = argparse.ArgumentParser(
        prog='py2uml',
        description='py2puml v' + __version__ +
        '\nby Michelle Baert, based on work from Martin B. K. Grønholdt.\n\n' +
        '    Create PlantUML classes from Python source code.',
        epilog='If no config file is provided, settings are loaded\n' +
        'sequentially from all available files in :\n' +
        '      - <PROGRAM_DIR>/py2puml.ini\n' +
        '      - <USER_HOME>/.config/py2puml.ini\n' +
        '      - <USER_HOME>/.py2puml.ini\n' +
        '      - <WORK_DIR>/.py2puml.ini\n' +
        '      - <WORK_DIR>/py2puml.ini\n' +
        '\nIf the provided config filename cannot be found,\n' +
        'the program will use no config at all.\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config',
                        help='Configuration file (replace defaults)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='The name of the ouput PlantUML file.')
    parser.add_argument('-r', '--root', #default='',
                        help='Project root directory.'
                        ' Create namespaces from there')
    parser.add_argument('py_file', nargs='+',
                        help='the Python source files to parse.')
    return parser

def run(cl_args):
    """Main application runner.

    @param cl_args: argparser namespace.
    """
    logger.info("Running with args: %r", cl_args)

    # Load configuration
    cfg = configparser.ConfigParser()
    if cl_args.config:
        # provided config file completely replaces global settings
        cfg.read(cl_args.config)
    else:
        cfg.read(CONFIG_FILENAMES)
    logger.info("Using config: %r",
                {s: {o:v for o, v in cfg.items(s)} for s, o in cfg.items()})

    # setup .puml generator
    if cl_args.root:
        gen = PUML_Generator_NS(dest=cl_args.output,
                                root=cl_args.root,
                                config=cfg)
    else:
        gen = PUML_Generator(dest=cl_args.output,
                             config=cfg)

    gen.header()
    for srcfile in cl_args.py_file:
        gen.do_file(srcfile, "Skipping file")

    gen.footer()
    # TODO detect and warn about empty results
    if cl_args.output != sys.stdout: # pragma: no cover
        cl_args.output.close()

if __name__ == '__main__': # pragma: no cover
    run(cli_parser().parse_args())
