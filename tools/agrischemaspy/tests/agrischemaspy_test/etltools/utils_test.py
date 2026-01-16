from agrischemaspy.etltools.utils import DEFAULT_NAMESPACES, normalize_rows_source
from agrischemaspy.etltools.utils import download_files

from brandizpyes.logging import logger_config
from brandizpyes.ioutils import dump_output

import unittest, os
from os.path import dirname, abspath, exists, getsize
from rdflib.namespace import RDFS
import importlib
import sys
import io
import logging

_TEST_DIR = os.path.abspath (
	os.path.dirname (  __file__ ) + "/../../resources/etltools/"
)


class XNamespaceManagerTest ( unittest.TestCase ):

	def test_uri ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.uri ( "ex:test" ), "http://www.example.com/ns/test", "uri() didn't work!" )
	
	def test_uri_chunks ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.uri ( "rdfs", "label" ), str ( RDFS ) + "label", "rdfs:label didn't work!" )

	def test_ns ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.ns ( 'schema' ), "https://schema.org/", "ns(schema) didn't work!" )

	def test_ns_two_colon ( self ):
		self.assertEqual( DEFAULT_NAMESPACES.ns ( 'ex:' ), "http://www.example.com/ns/", "ns(ex:) didn't work!" )

	def test_to_sparql ( self ):
		self.assertTrue (
			"PREFIX schema: <https://schema.org/>\n" in DEFAULT_NAMESPACES.to_sparql (),
			"to_sparql() didn't work!"
		)

	def test_to_turtle ( self ):
		self.assertTrue (
			"prefix schema: <https://schema.org/>\n" in DEFAULT_NAMESPACES.to_turtle (),
			"to_turtle() didn't work!"
		)

	def test_ns_path ( self ):
		# To make the module pick the new NS file, we need to reload it
		from agrischemaspy.etltools import utils as utl
		os.environ[ 'NAMESPACES_PATH' ] = _TEST_DIR + "/test-namespaces.ttl"
		importlib.reload ( utl )
		self.assertEqual( utl.DEFAULT_NAMESPACES.ns ( 'foo:' ), "http://www.foo.com/ns/", "NAMESPACES_PATH didn't work!" )


def process_rows ( rows_src ):
	l = 0; res = "";
	for row in normalize_rows_source ( rows_src ):
		res += "L:%d, Name:%s, Surname:%s\n" % ( l, row [ 0 ], row [ 1 ] )
		l += 1
	return res

class ProcessDocRowsTest ( unittest.TestCase ):
	
	def test_list ( self ):
		r = process_rows ( [ ["John", "Smith"], ["Karl", "Marx"], ["Emmanuel", "Kant"] ] )
		self.assertTrue ( "Expected string not found in the result!", "L:1, Name: Karl, Surname: Marx" in r )
	
	def test_file ( self ):
		r = process_rows (  _TEST_DIR + "/test.tsv" )
		self.assertTrue ( "Expected string not found in the result!", "L:2, Name: Charles, Surname: Babbage" in r )
	

class TestDownloadFiles ( unittest.TestCase ):
	def test_basics ( self ):
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		
		download_files ( "https://schema.org/version/latest/schemaorg-current-https.ttl", "/tmp/schema.ttl", "schema.org" )
		self.assertTrue ( exists ( "/tmp/schema.ttl" ), "test file not downloaded!" )

	def test_multi ( self ):
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		if exists ( "/tmp/dcterms.ttl" ): os.remove ( "/tmp/dcterms.ttl" )

		download_files ( 
			[{ "url": "https://schema.org/version/latest/schemaorg-current-https.ttl", 
			  "out": "schema.ttl" },
			{ "url": "http://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl", 
			  "out": "dcterms.ttl" }],
			out_dir = "/tmp"
		)

		self.assertTrue ( exists ( "/tmp/schema.ttl" ), "test file not downloaded (schema)!" )
		self.assertTrue ( exists ( "/tmp/dcterms.ttl" ), "test file not downloaded (dcterms)!" )

	def test_multi_positional_params ( self ):
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		if exists ( "/tmp/dcterms.ttl" ): os.remove ( "/tmp/dcterms.ttl" )

		download_files ( 
			[[ "https://schema.org/version/latest/schemaorg-current-https.ttl", 
			  "schema.ttl" ],
			[ "http://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl", 
			  "dcterms.ttl" ]],
			out_dir = "/tmp"
		)

		self.assertTrue ( exists ( "/tmp/schema.ttl" ), "test file not downloaded (schema)!" )
		self.assertTrue ( exists ( "/tmp/dcterms.ttl" ), "test file not downloaded (dcterms)!" )

	def test_overwrite ( self ):
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		dump_output ( lambda out: print ( "1", file = out ), "/tmp/schema.ttl" )
		
		download_files (
			"https://schema.org/version/latest/schemaorg-current-https.ttl", "/tmp/schema.ttl", "new schema.org", 
			overwrite = True
		)
		
		self.assertTrue ( getsize ( "/tmp/schema.ttl" ) > 1000, "overwrite flag didn't work" )


		
if __name__ == '__main__':
	logger_config ()
	unittest.main()
