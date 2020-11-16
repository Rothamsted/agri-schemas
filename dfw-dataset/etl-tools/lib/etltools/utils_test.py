from etltools.utils import DEFAULT_NAMESPACES, process_doc_rows
import unittest, os
from os.path import dirname, abspath
from rdflib.namespace import RDFS
import importlib


class XNamespaceManagerTest ( unittest.TestCase ):

	def test_uri ( self ):
	  self.assertEqual( DEFAULT_NAMESPACES.uri ( "ex:test" ), "http://www.example.com/ns/test", "uri() didn't work!" )
	
	def test_uri_chunks ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.uri ( "rdfs", "label" ), str ( RDFS ) + "label", "rdfs:label didn't work!" )

	def test_ns ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.ns ( 'schema' ), "http://schema.org/", "ns(schema) didn't work!" )

	def test_ns_two_colon ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.ns ( 'schema:' ), "http://schema.org/", "ns(schema:) didn't work!" )

	def test_to_sparql ( self ):
		self.assertTrue (
			"PREFIX schema: <http://schema.org/>\n" in DEFAULT_NAMESPACES.to_sparql (),
			"to_sparql() didn't work!"
		)

	def test_to_turtle ( self ):
		self.assertTrue (
			"prefix schema: <http://schema.org/>\n" in DEFAULT_NAMESPACES.to_turtle (),
			"to_turtle() didn't work!"
		)

	def test_ns_path ( self ):
		from etltools import utils as utl
		os.environ[ 'NAMESPACES_PATH' ] = dirname ( abspath ( __file__ ) ) + "/test-namespaces.ttl"
		importlib.reload ( utl )
		self.assertEqual( utl.DEFAULT_NAMESPACES.ns ( 'foo:' ), "http://www.foo.com/ns/", "NAMESPACES_PATH didn't work!" )


def process_rows ( rows_src ):
	l = 0; res = "";
	for row in process_doc_rows ( rows_src ):
		res += "L:%d, Name:%s, Surname:%s\n" % ( l, row [ 0 ], row [ 1 ] )
		l += 1
	return res

class ProcessDocRowsTest ( unittest.TestCase ):
	
	def test_list ( self ):
		r = process_rows ( [ ["John", "Smith"], ["Karl", "Marx"], ["Emmanuel", "Kant"] ] )
		self.assertTrue ( "Expected string not found in the result!", "L:1, Name: Karl, Surname: Marx" in r )
	
	def test_file ( self ):
		r = process_rows ( os.path.abspath ( os.path.dirname( __file__ ) + "/test.tsv" ) )
		self.assertTrue ( "Expected string not found in the result!", "L:2, Name: Charles, Surname: Babbage" in r )
	
					
if __name__ == '__main__':
  unittest.main()
