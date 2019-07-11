import argparse
import json
import os
import logging
from relational_compiler import RelationalCompiler
from jinja2 import Template
from jsonpath_rw import jsonpath, parse
from pyld import jsonld

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

class APICompiler(RelationalCompiler):

    """ Given a bag of tabular data, generate a web service API with a relational database back end. """
    def __init__(self, bag_archive, output_path="out", generated_path="gen"):
        super(APICompiler,self).__init__(
            bag_archive=bag_archive,
            output_path=output_path,
            generated_path=generated_path)

    def _gen_name (self, path):
        """ Generate a path relative to the output directory. """
        return os.path.join (self.generated_path, path)

    def compile (self, options_path=None):
        """ Compile the given bag to emit an OpenAPI server backed by a relational data store.
           :param: bag BDBag archive to compile.
           :param: output_path Output directory to emit generated sources to.
           :param: options_path Settings for generated system as JSON object.
        """

        """ Generate the relational back end. """
        super(APICompiler,self).compile (options_path)
        
        """ Get the template we'll use to emit the service endpoint. """
        template = self._get_app_template (self.options)
        dataset_server_file_name = os.path.join (self.generated_path, "server.py")
        print ("-- {}".format (dataset_server_file_name))

        with open(dataset_server_file_name, "w") as app_code:
            app_code.write (template.render (
                datasets=self.dataset_dbs,
                options=self.options))

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

    output_path = generated_path = os.path.join(args.out, "gen")

    """ Create an API compiler givren the input bag. """
    compiler = APICompiler (
        bag_archive=args.bag,
        output_path=args.out,
        generated_path=generated_path)

    """ Compile the service. """
    compiler.compile (options_path=args.opts)
