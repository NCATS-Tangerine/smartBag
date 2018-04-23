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
    def __init__(self, generated_path="gen"):
        self.generated_path = generated_path
        if not os.path.exists (self.generated_path):
            os.makedirs (self.generated_path)

    def _gen_name (self, path):
        """ Generate a path relative to the output directory. """
        return os.path.join (self.generated_path, path)

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

    def _generate_relational_database (self, csv_file):
        db_basename = os.path.basename (csv_file).\
                      replace (".csv", ".sqlitedb").\
                      replace ("-", "_")
        sql_db_file = self._gen_name (db_basename)

        if os.path.exists (sql_db_file):
            print (" -- {0} already exists. skipping.".format (sql_db_file))
            return

        dataset = None

        with open(csv_file, 'r') as stream:
            #stream.read (1)
            reader = csv.reader (stream)
            #reader = csv.reader (filter(lambda row: row[0] != '#', stream))
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

    def compile (self, bag, output_path=".", options_path=None):
        """ Compile the given bag to emit an OpenAPI server backed by a relational data store.
           :param: bag BDBag archive to compile.
           :param: output_path Output directory to emit generated sources to.
           :param: options_path Settings for generated system as JSON object.
        """

        """ Load options. """
        options = {}
        if options_path:
            with open(options_path, "r") as stream:
                options = json.loads(stream.read ())

        """ Parse bag manifest. """
        manifest = self.parse (
            bag_archive=args.bag,
            output_path=args.out)

        """ Process each data set in the bag. """
        dataset_dbs = []
        for dataset in manifest['datasets']:
            dataset_base = os.path.basename (dataset)
            ds = self._generate_relational_database (dataset)
            assert ds, (f"Error generating relational data for {dataset}.")
            ds.jsonld_context = manifest['datasets'][dataset]['@context']
            ds.jsonld_context_text = json.dumps (ds.jsonld_context, indent=2)
            dataset_dbs.append (ds)
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

            """ Get the template we'll use to emit the service endpoint. """
            template = self._get_app_template (options)
            dataset_server_file_name = os.path.join (self.generated_path, "server.py")
            print ("-- {}".format (dataset_server_file_name))
            with open(dataset_server_file_name, "w") as app_code:
                app_code.write (template.render (
                    datasets=dataset_dbs,
                    options=options))

    def _get_app_template(self, options):
        """ Configure the application template to use for generating the service endpoint. """
        template = None
        app_template=options.get("app_template", "app.py.j2")
        if not app_template.startswith (os.path.sep):
            source_dir = os.path.dirname(__file__)
            app_template = os.path.join (source_dir, app_template)
        with open(app_template, "r") as stream:
            template = Template (stream.read ())
        return template
    
class SemanticCrunch:

    def apply_semantic_mapping (jsonld_context):
        """ Expand the context with JSON-LD """
        jsonld_context = json.loads (json.dumps (service_metadata.jsonld),
                                     parse_float=lambda v : str (v))
        del jsonld_context['@context']['@version']
        expanded = jsonld.expand (
            response,
            {
                "expandContext" : jsonld_context['@context']
            })
        """ Parse the JSON-LD expanded response with JSON-Path. """
        json_path_expr = parse (method_metadata.path)
        result_vals = [ match.value
                        for match in json_path_expr.find (expanded)
                        if match.value.startswith (method_metadata.out_type) ]

if __name__ == "__main__":
    
    '''
    Parse command line arguments
    Unpack a bdbag
    Identify the data files
    For each data file
      Load and the associated jsonld context
      Use it to determine columns in the data set
      Generate relational database tables
    Generate a openapi/smartapi server to publish the data
      TODO: Implement simple (two table) relational query
    '''

    parser = argparse.ArgumentParser(description='SmartBag.')
    parser.add_argument('-b', '--bag', help='Bag to parse.', default="test_bag.tgz")
    parser.add_argument('-o', '--out', help='Output directory.', default="out")
    parser.add_argument('-p', '--opts', help='Compiler options', default=None)
    args = parser.parse_args()

    output_path = generated_path=os.path.join(args.out, "gen")
    compiler = APICompiler (output_path)
    compiler.compile (
        bag=args.bag,
        output_path=args.out,
        options_path=args.opts)
