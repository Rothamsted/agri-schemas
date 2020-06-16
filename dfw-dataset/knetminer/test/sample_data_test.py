import os, sys
from os.path import dirname, abspath
from etltools import sparulmap
from etltools.utils import get_jena_home, sparql_ask
import rdflib
import unittest

graph = None

def run_mappings ():
	global graph
	if graph: return
	graph = rdflib.Graph()

	mydir = dirname ( abspath ( __file__ ) )
	os.chdir ( mydir )
		
	print ( "Running mapping workflow" )
	if os.system ( "snakemake --snakefile sample-data-build.snakefile --configfile ../../snake-config.yaml" ) != 0:
		raise ChildProcessError ( "Mapping workflow execution failed" )
	
	out_path = os.getenv ( "ETL_OUT" ) + "/test/knetminer-mapping-test-out.ttl"
	print ( "--- Loading result from '%s'" % out_path )
	graph.parse ( out_path, format = "turtle" )	

	print ( "----- Test Initialised -----\n\n" )
	

class KnetSampleDataTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		run_mappings ()
		super().__init__ ( methodName )

	def assert_sparql ( self, ask_query, msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), msg )

	def test_schema_name ( self ):
		self.assert_sparql ( 
			"""
			ASK { 
				BIND ( "Probable trehalose-phosphate phosphatase 1" AS ?testName )
				?protein bk:prefName ?testName; schema:name ?testName.
			}
			""",
			"schema:name not inferred from bk:prefName!"
		)


if __name__ == '__main__':
	unittest.main()
