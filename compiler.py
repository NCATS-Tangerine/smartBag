import argparse
import csv
import glob
import json
import os
import sqlite3
import logging
import sys
import gzip
from bdbag import bdbag_api
from jinja2 import Template
from jsonpath_rw import jsonpath, parse
from pyld import jsonld

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

class Column:
    """ Model a table column. """
    def __init__(self, name, column_type=None):
        self.name = name
        self.type = column_type
    def __repr__(self):
        return "{0} {1}".format (self.name, self.type)

class DataSet:
    """ A set of columns and associated metadata. """
    def __init__(self, db_path, columns):
        self.name = db_path.replace (".sqlitedb", "")
        self.db_path = db_path
        self.columns = columns
        self.operations = []
        self.jsonld_context = {}
        self.example_rows = []
    def __repr__(self):
        return "{0} {1} {2}".format (self.name, self.db_path, self.columns)

class CSVFilter:
    """ Implement data set specific filters. Generalize. """
    def filter_data (self, f):
        basename = os.path.basename (f)
        if basename.startswith ("CTD_") or basename.startswith ("Bicl"):
            with open (f, "r") as stream:
                f_new = "{0}.new".format (f)
                with open (f_new, "w") as new_stream:
                    headers_next = False
                    index = 0
                    for line in stream:
                        index = index + 1
                        out_line = line
                        if line.startswith ("#"):
                            if headers_next:
                                out_line = line.replace ("# ", "")
                                headers_next = False
                            elif line.strip() == "# Fields:":
                                out_line = None
                                headers_next = True
                            else:
                                out_line = None
                        if out_line:
                            new_stream.write (out_line)
            os.rename (f_new, f)

class BagCompiler:
    """ Demarcates generic concepts relating to compiling a bag. """
    def compile (self, manifest, options):
        raise ValueError ("Not implemented")
    def parse (self, bag_archive, output_path="out"):
        raise ValueError ("Not implemented.")
    def cleanup_bag (bag_path):
        bdbag_api.cleanup_bag (os.path.dirname (bag_path))
