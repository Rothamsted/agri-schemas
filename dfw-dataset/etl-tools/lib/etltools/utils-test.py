from etltools.utils import XNamespaceManager, DEFAULT_NAMESPACES
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

if __name__ == '__main__':
  unittest.main()
