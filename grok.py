import csv
import glob
import json
import os
import sqlite3
import sys
import gzip
from bdbag import bdbag_api
from jinja2 import Template
from jsonpath_rw import jsonpath, parse
from pyld import jsonld

class DataSet:
    def __init__(self, db_path, columns):
        self.name = db_path.replace (".sqlitedb", "")
        self.db_path = db_path
        self.columns = columns
        self.operations = []

class CSVFilter:
    """ Implement data set specific filters. """
    def filter_data (self, f):
        basename = os.path.basename (f)
        if basename.startswith ("CTD_"):
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
            
class BagServer:

    def __init__(self, generated_path="gen"):
        self.generated_path = generated_path
        if not os.path.exists (self.generated_path):
            os.makedirs (self.generated_path)
            
    def gen_name (self, path):
        return os.path.join (self.generated_path, path)
    
    def csv_to_sql (self, csv_file):
        db_basename = os.path.basename (csv_file).\
                      replace (".csv", ".sqlitedb").\
                      replace ("-", "_")
        sql_db_file = self.gen_name (db_basename)

        if os.path.exists (sql_db_file): 
            print (" -- {0} already exists. skipping.".format (sql_db_file))
            return
        
        dataset = None
        
        with open(csv_file, 'r') as stream:
            #stream.read (1)
            reader = csv.reader (stream)
            #reader = csv.reader (filter(lambda row: row[0] != '#', stream))
            headers = next (reader)
            dataset = DataSet (db_basename, headers)

            sql = sqlite3.connect (sql_db_file)
            cur = sql.cursor ()
            table_name = os.path.basename (csv_file.
                                           replace (".csv", "").
                                           replace ("-", "_"))
            col_types = ', '.join ([ "{0} text".format (col) for col in headers ])
            create_table = "CREATE TABLE IF NOT EXISTS {0} ({1})".format (
                table_name, col_types)
            print (create_table)
            cur.execute (create_table)
            
            col_wildcards = ', '.join ([ "?" for col in headers ])
            insert_command = "INSERT INTO {0} VALUES ({1})".format (
                table_name, col_wildcards)
            print (insert_command)
            for row in reader:
                print (row)
                values = [ r for r in row ]
                print (values)
                cur.execute (insert_command, row)

            sql.commit()
            sql.close ()
        return dataset

    def serve (self, manifest, app_template="app.py.j2"):
        dataset_dbs = []
        if not app_template.startswith (os.path.sep):
            source_dir = os.path.dirname(__file__)
            app_template = os.path.join (source_dir, app_template)

        for dataset in manifest['datasets']:
            dataset_base = os.path.basename (dataset)
            dataset_dbs.append (self.csv_to_sql (dataset))
            with open(app_template, "r") as stream:                
                template = Template (stream.read ())
                dataset_server = self.gen_name (
                    "{0}.py".format (dataset_base.\
                                     replace (".csv", "").\
                                     replace ("-", "_")))
                print ("-- {}".format (dataset_server))
                with open(dataset_server, "w") as app_code:
                    app_code.write (template.render (datasets=dataset_dbs))

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

    def grok_bag (self, bag_archive, output_path="out"):
        manifest = {}
        bag_path = bdbag_api.extract_bag (bag_archive, output_path=output_path)
        if bdbag_api.is_bag(bag_path):
            manifest['path'] = bag_path
            manifest['datasets'] = {}
            datasets = manifest['datasets']
            data_path = os.path.join (bag_path, "data")
            tar_data_files = glob.glob (os.path.join (data_path, "*.csv.gz"))
            for f in tar_data_files:
                with gzip.open(f, 'rb') as zipped:
                    extracted = f.replace (".gz", "")
                    with open (extracted, "wb") as stream:
                        file_content = zipped.read ()
                        stream.write (file_content)

            data_files = glob.glob (os.path.join (data_path, "*.csv"))
            csv_filter = CSVFilter ()
            for f in data_files:
                csv_filter.filter_data (f)
                print ("  -- file: {}".format (f))
                jsonld_context_file = "{0}.jsonld".format (f)
                if os.path.exists (jsonld_context_file):
                    with open (jsonld_context_file, "r") as stream:
                        datasets[f] = json.loads (stream.read ())
                        context = datasets[f]['@context']
                        datasets[f]['columns'] = [ k for k in context ]
        return manifest

    def cleanup_bag (bag_path):
        bdbag_api.cleanup_bag (os.path.dirname (bag_path))

# bdbag ./test_bag/ --update --validate fast --validate-profile --archive tgz

if __name__ == "__main__":
    '''
    unpack a bdbag
    identify the data files
    for each data file
      load and the associated jsonld context
      use it to determine columns in the data set
    '''
    bag = sys.argv[1] if len (sys.argv) > 1 else "test_bag.tgz"
    output_dir = sys.argv[2] if len (sys.argv) > 2 else "out"

    sc = SemanticCrunch ()
    manifest = sc.grok_bag (
        bag_archive=bag,
        output_path=output_dir)
    print (json.dumps (manifest, indent=2))

    server = BagServer ()
    server.serve (manifest)
