import argparse
import csv
import glob
import json
import os
import sqlite3
import logging
import sys
import gzip
from compiler import BagCompiler
from compiler import Column
from compiler import DataSet
from compiler import CSVFilter
from bdbag import bdbag_api
from jinja2 import Template
from jsonpath_rw import jsonpath, parse
from pyld import jsonld

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

class RelationalCompiler(BagCompiler):
    """ Given a bag of tabular data, generate a relational database back end for it. """
    def __init__(self, bag_archive, output_path, generated_path="gen"):
        super(RelationalCompiler,self).__init__(
            bag_archive,
            output_path=output_path,
            generated_path=generated_path)
        self.dataset_dbs = []

    def _gen_name (self, path):
        """ Generate a path relative to the output directory. """
        return os.path.join (self.generated_path, path)

    def _generate_relational_database (self, csv_file):
        """ Generate a relational table. """
        db_basename = os.path.basename (csv_file).\
                      replace (".csv", ".sqlitedb").\
                      replace ("-", "_")
        sql_db_file = self._gen_name (db_basename)

        if os.path.exists (sql_db_file):
            print (" -- {0} already exists. skipping.".format (sql_db_file))
            return

        dataset = None

        with open(csv_file, 'r') as stream:
            reader = csv.reader (stream)
            headers = next (reader)
            columns = { n : Column(n, None) for n in headers }
            dataset = DataSet (db_basename, columns)

            sql = sqlite3.connect (sql_db_file)
            sql.text_factory = str
            cur = sql.cursor ()
            table_name = os.path.basename (csv_file.
                                           replace (".csv", "").
                                           replace ("-", "_"))
            col_types = ', '.join ([ "{0} text".format (col) for col in headers ])
            col_types = col_types.replace("#", "")
            create_table = "CREATE TABLE IF NOT EXISTS {0} ({1})".format (
                table_name, col_types)
            print (create_table)
            cur.execute (create_table)

            col_wildcards = ', '.join ([ "?" for col in headers ])
            insert_command = "INSERT INTO {0} VALUES ({1})".format (
                table_name, col_wildcards)
            print (insert_command)
            i = 0
            max_examples = 5
            for row in reader:
                #print (row)
                values = [ r for r in row ]
                if i < max_examples:
                    print (values)
                    dataset.example_rows.append (values)
                    i = i + 1
                cur.execute (insert_command, row)
            sql.commit()
            sql.close ()
        return dataset

    def compile (self, options_path=None):
        """ Compile the given bag to emit an OpenAPI server backed by a relational data store.
           :param: bag BDBag archive to compile.
           :param: output_path Output directory to emit generated sources to.
           :param: options_path Settings for generated system as JSON object.
        """

        """ Load options. """
        """ Generate the relational back end. """
        super(RelationalCompiler,self).compile (options_path)

        """ Process each data set in the bag. """
        for dataset in self.manifest['datasets']:
            dataset_base = os.path.basename (dataset)
            ds = self._generate_relational_database (dataset)
            assert ds, (f"Error generating relational data for {dataset}.")
            ds.jsonld_context = self.manifest['datasets'][dataset]['@context']
            ds.jsonld_context_text = json.dumps (ds.jsonld_context, indent=2)
            self.dataset_dbs.append (ds)
            for name, column in ds.columns.items ():
                column_type = ds.jsonld_context.get (column.name, {}).get ('@type', None)
                if column_type:
                    if not column_type.startswith ('http') and ':' in column_type:
                        vals = column_type.split (':')
                        curie = vals[0]
                        value = vals[1]
                        iri = ds.jsonld_context[curie]
                        column_type = "{0}{1}".format (iri, value)
                    ds.columns[name] = Column (name, column_type)
                    print ("col: {} {} ".format (name, ds.columns[name].type))
    
