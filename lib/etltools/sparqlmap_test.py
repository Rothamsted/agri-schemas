import unittest
from etltools import sparqlmap
from etltools.utils import get_jena_home, sparql_ask, DEFAULT_NAMESPACES
import os, shutil
from os.path import dirname, abspath

import sh

import rdflib

# Don't do it this way in production, use NAMESPACES_PATH
DEFAULT_NAMESPACES.bind ( 'ex1', 'http://www.example.com/ns1/', True, True )

graph = None
is_initialized = False

def run_mappings ():
	global is_initialized
	if is_initialized: return
	
	global graph
	graph = rdflib.Graph()

	mydir = dirname ( abspath ( __file__ ) )

	test_tdb_path = '/tmp/sparql-mapping-test-tdb'
	test_data_path = mydir + "/test-data.ttl"
	out_path = "/tmp/sparqlmap-out.nt"

	if os.path.exists ( test_tdb_path ): shutil.rmtree ( test_tdb_path )
	os.mkdir ( test_tdb_path )

	print ( "--- Loading test data on '%s'" % test_tdb_path )
	
	tdb_sh = sh.Command ( get_jena_home () + "/bin/tdbloader" )
	tdb_sh ( "--loc=%s" % test_tdb_path, test_data_path )
	
	sparql_vars = { 'SRC_NAMESPACE': 'ex:' }

	print ( "--- Running the mapper " )
	sparqlmap.map_from_files ( 
		mydir + "/map-rules", test_tdb_path, out_path, sparql_vars
	)

	print ( "--- Loading result from '%s'" % out_path )
	graph.parse ( out_path, format = "turtle" )	

	is_initialized = True
	print ( "----- Test Initialised -----\n\n" )
	

class SparulMapTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		run_mappings ()
		super().__init__ ( methodName )

	def assert_sparql ( self, ask_query, msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query, DEFAULT_NAMESPACES ), msg )

	def test_subclass ( self ):
		self.assert_sparql ( "ASK { ex:b a ex1:SuperB }", "super-class not inferred!" )

	def test_eq_class ( self ):
		self.assert_sparql ( "ASK { ex:a a schema:Thing }", "ex:a equivalent class not inferred!" )
	
	def test_sub_prop ( self ):
		self.assert_sparql ( "ASK { ex:component1 schema:partOf ex:container }", "super-property not inferred!" )

	def test_eq_prop ( self ):
		self.assert_sparql ( "ASK { ex:a schema:sameAs ex:b }", "ex:a equivalent property not inferred!" )

	def test_inverse_prop ( self ):
		self.assert_sparql ( "ASK { ex:component2 schema:partOf ex:container }", "inverse property not inferred" )

	def test_no_inference ( self ):
		self.assert_sparql ( 
			"ASK { FILTER NOT EXISTS {ex:container schema:hasPart ex:component1}}", "Unexpected inference!"
		)


if __name__ == '__main__':
	unittest.main()
