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
    def __init__(self, bag_archive, output_path="out", generated_path="gen"):
        self.generated_path = generated_path
        if not os.path.exists (self.generated_path):
            os.makedirs (self.generated_path)
        """ Parse bag manifest. """
        self.manifest = self.parse (
            bag_archive=bag_archive,
            output_path=output_path)
        self.options = None
    def get_options(self, options_path):
        options = {}
        if options_path:
            with open(options_path, "r") as stream:
                options = json.loads(stream.read ())
        return options
    def compile (self, options_path):
        """ Load options. """
        self.options = self.get_options (options_path)
    def parse (self, bag_archive, output_path="out"):
        """ Analyze the bag, consuming BagIt-RO metadata into a structure downstream code emitters can use. """
        manifest = {}
        """ Extract the bag. """
        bag_path = bdbag_api.extract_bag (bag_archive, output_path=output_path)
        if bdbag_api.is_bag(bag_path):

            logger.debug ("Initializing metadata datasets")
            manifest['path'] = bag_path
            manifest['datasets'] = {}
            datasets = manifest['datasets']
            data_path = os.path.join (bag_path, "data")

            """ Extract tarred files. """
            tar_data_files = glob.glob (os.path.join (data_path, "*.csv.gz"))
            for f in tar_data_files:
                with gzip.open(f, 'rb') as zipped:
                    extracted = f.replace (".gz", "")
                    with open (extracted, "wb") as stream:
                        file_content = zipped.read ()
                        stream.write (file_content)

            """ Collect metadata for each file. """
            data_files = glob.glob (os.path.join (data_path, "*.csv"))
            csv_filter = CSVFilter ()
            for f in data_files:
                csv_filter.filter_data (f)
                logger.debug (f"  --collecting metadata for: {f}")
                jsonld_context = self._get_jsonld_context (f)
                datasets[f] = jsonld_context
                context = datasets[f]['@context']
                datasets[f]['columns'] = {
                    k : None for k in context if isinstance(context[k],dict)
                }
        return manifest
    def _get_jsonld_context (self, data_file):
        jsonld = None
        ro_model_path = data_file.split (os.path.sep)
        ro_model_path.insert (-1, os.path.sep.join ([ '..', 'metadata', 'annotations' ]))
        ro_model_path = os.path.sep.join (ro_model_path)

        jsonld_context_files = [
            "{0}.jsonld".format (data_file),
            "{0}.jsonld".format (ro_model_path)
        ]
        for jsonld_context_file in jsonld_context_files:
            print ("testing {}".format (jsonld_context_file))
            if os.path.exists (jsonld_context_file):
                print ("opening {}".format (jsonld_context_file))
                with open (jsonld_context_file, "r") as stream:
                    jsonld = json.loads (stream.read ())
                    break
        return jsonld
    def cleanup_bag (bag_path):
        bdbag_api.cleanup_bag (os.path.dirname (bag_path))
