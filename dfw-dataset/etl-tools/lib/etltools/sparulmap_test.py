import unittest
from etltools import sparulmap
from etltools.utils import get_jena_home, sparql_ask
from subprocess import run
import os, shutil
from os.path import dirname, abspath

import rdflib

graph = None

def run_mappings ():
	global graph
	if graph: return
	
	graph = rdflib.Graph()

	mydir = dirname ( abspath ( __file__ ) )

	test_tdb_path = '/tmp/sparul-mapping-test-tdb'
	test_data_path = mydir + "/test-data.ttl"
	out_path = "/tmp/sparulmap-out.ttl"

	if os.path.exists ( test_tdb_path ): shutil.rmtree ( test_tdb_path )
	os.mkdir ( test_tdb_path )

	print ( "--- Loading test data on '%s'" % test_tdb_path )
	proc = run ( 
		[ get_jena_home () + "/bin/tdbloader", "--loc=%s" % test_tdb_path, test_data_path ], 
		text = True
	)
	if proc.returncode != 0:
		raise ChildProcessError ( "Error #%d while preparing test TDB " % proc.returncode )

	sparql_vars = { 'TARGET_NAMESPACE': 'schema:' }

	print ( "--- Running the mapper " )
	sparulmap.map_from_files ( 
		mydir + "/sparulmap-default-rules", test_tdb_path, "ex:mappedGraph", out_path, sparql_vars
	)

	print ( "--- Loading result from '%s'" % out_path )
	graph.parse ( out_path, format = "turtle" )	

	print ( "----- Test Initialised -----\n\n" )
	

class SparulMapTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		run_mappings ()
		super().__init__ ( methodName )

	def assert_sparql ( self, ask_query, msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), msg )

	def test_transitive_class ( self ):
		self.assert_sparql ( "ASK { ex:b a ex:A }", "ex:b a ex:A not inferred!" )

	def test_mapped_class ( self ):
		self.assert_sparql ( "ASK { ex:a a schema:Thing }", "ex:a direct owl:equivalentClass not mapped!" )
	
	def test_mapped_class_via_chain ( self ):
		self.assert_sparql ( "ASK { ex:b a schema:Thing }", "ex:b owl:equivalentClass/rdfs:subClassOf not mapped!"	)

	def test_transitive_prop ( self ):
		self.assert_sparql (
			"ASK { ex:container ex:hasPart ex:specialComponent }", 
			"ex:container ex:hasPart ex:specialComponent not inferred!"	
		)

	def test_mapped_prop ( self ):
		self.assert_sparql ( "ASK { ex:a schema:sameAs ex:b }", "ex:a direct owl:equivalentProperty not mapped!" )

	def test_mapped_prop_via_chain ( self ):
		self.assert_sparql ( 
			"ASK { ex:c schema:sameAs ex:b }",
			"ex:c direct owl:equivalentClass/rdfs:subClassOf not mapped!"
		)

	def test_mapped_prop_via_inverse ( self ):
		self.assert_sparql ( 
			"ASK { ex:component schema:partOf ex:container }", "inverseOf-based mapping not working!"
		)

	def test_mapped_prop_via_inverse_and_chain ( self ):
		self.assert_sparql ( 
			"ASK { ex:specialComponent schema:partOf ex:container  }", "mapping based on subproperty+inverse not working!"
		)


if __name__ == '__main__':
	unittest.main()
