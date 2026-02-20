from agrischemas.etltools.utils import DEFAULT_NAMESPACES, normalize_rows_source, XNamespaceManager
from agrischemas.etltools.utils import download_file, download_files

from brandizpyes.ioutils import dump_output

import unittest, os
from os.path import exists, getsize
from rdflib.namespace import RDFS
import importlib

from assertpy import assert_that

_TEST_DIR = os.path.abspath (
	os.path.dirname (  __file__ ) + "/../../resources/etltools/"
)


class TestXNamespaceManager:

	"""
	The tests implicitly test `load()` from a file, since that's used to populate the `DEFAULT_NAMESPACES`.
	"""

	def test_uri ( self ):
		assert_that( DEFAULT_NAMESPACES.uri ( "ex:test" ), "uri() works in base case" )\
			.is_equal_to( "http://www.example.com/ns/test" )
	
	def test_uri_chunks ( self ):
		assert_that( DEFAULT_NAMESPACES.uri ( "rdfs", "label" ), "uri() works for rdfs:label" )\
			.is_equal_to( str ( RDFS ) + "label" )
	def test_ns ( self ):
		assert_that( DEFAULT_NAMESPACES.ns ( 'schema' ), "ns(schema) works" )\
			.is_equal_to( "https://schema.org/" )

	def test_ns_two_colon ( self ):
		assert_that( DEFAULT_NAMESPACES.ns ( 'ex:' ), "ns(ex:) works" )\
			.is_equal_to( "http://www.example.com/ns/" )

	def test_ns_empty_ns ( self ):		
		"""
		Tests the ':' prefix, which should work with the two colon only, or with the empty string. 
		"""
		ns_uri = "http://www.example.com/foo/default/"
		ns_mgr = XNamespaceManager ()
		ns_mgr.bind ( "", ns_uri )

		assert_that( ns_mgr.ns ( ':' ), "ns(:) works" ).is_equal_to( ns_uri )
		assert_that( ns_mgr.uri ( ":Blah" ), "uri(:Blah) works" ).is_equal_to( ns_uri + "Blah" )
		assert_that( ns_mgr.ns ( '' ), "ns('') works" ).is_equal_to( ns_uri )
		# This should not be equal to :Blah, cause it's not how namespaces are normally used
		assert_that( ns_mgr.uri ( 'Blah' ), "uri('Blah') is returned untouched" ).is_equal_to( "Blah" )

	def test_to_sparql ( self ):
		assert_that (
			"PREFIX schema: <https://schema.org/>\n" in DEFAULT_NAMESPACES.to_sparql (),
			"to_sparql() works"
		).is_true ()

	def test_to_turtle ( self ):
		assert_that (
			"prefix schema: <https://schema.org/>\n" in DEFAULT_NAMESPACES.to_turtle (),
			"to_turtle() works"
		).is_true ()

	def test_ns_path ( self ):
		# To make the module pick the new NS file, we need to reload it
		from agrischemas.etltools import utils as utl
		os.environ[ 'NAMESPACES_PATH' ] = _TEST_DIR + "/test-namespaces.ttl"
		importlib.reload ( utl )
		assert_that( utl.DEFAULT_NAMESPACES.ns ( 'foo:' ), "NAMESPACES_PATH works" )\
			.is_equal_to( "http://www.foo.com/ns/" )

	def test_load_from_string ( self ):
		ex_ns, ex2_ns = "http://www.example.com/ns/", "http://www.example.com/ns2/"
		ns_mgr = XNamespaceManager ()
		ns_mgr.load ( data = f"""
			@prefix ex: <{ex_ns}> .
			@prefix ex2: <{ex2_ns}> .
		""", rdf_format = "turtle" )
		assert_that( ns_mgr.ns ( 'ex:' ), "load from string works for ex" ).is_equal_to( ex_ns )
		assert_that( ns_mgr.ns ( 'ex2:' ), "load from string works for ex2" ).is_equal_to( ex2_ns )



class TestNormalizeRowsSource:

	@staticmethod
	def process_rows ( rows_src ):
		l = 0; res = "";
		for row in normalize_rows_source ( rows_src ):
			res += "L:%d, Name:%s, Surname:%s\n" % ( l, row [ 0 ], row [ 1 ] )
			l += 1
		return res


	@staticmethod
	def test_list ():
		r = TestNormalizeRowsSource.process_rows ( [ ["John", "Smith"], ["Karl", "Marx"], ["Emmanuel", "Kant"] ] )
		assert_that (
			r,
			"Expected string found in the result"
		).contains ( "L:1, Name:Karl, Surname:Marx" )

	@staticmethod
	def test_file ():
		r = TestNormalizeRowsSource.process_rows (  _TEST_DIR + "/test.tsv" )
		assert_that (
			r,
			"Expected string found in the result"
		).contains ( "L:2, Name:Charles, Surname:Babbage" )
	

class TestDownloadFiles:
	
	@staticmethod
	def test_basics ():
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		
		download_file ( "https://schema.org/version/latest/schemaorg-current-https.ttl", "/tmp/schema.ttl", "schema.org" )
		assert_that ( exists ( "/tmp/schema.ttl" ), "Test file downloaded" ).is_true ()

	@staticmethod
	def test_multi ():
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		if exists ( "/tmp/dcterms.ttl" ): os.remove ( "/tmp/dcterms.ttl" )

		download_files (
			[{ 
				"url": "https://schema.org/version/latest/schemaorg-current-https.ttl", 
				"out": "schema.ttl" 
			},
			{ 
				"url": "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl", 
			  "out": "dcterms.ttl",
				"user_agent": ""
			}],
			out_dir = "/tmp"
		)

		assert_that ( exists ( "/tmp/schema.ttl" ), "Test file downloaded (schema)" ).is_true ()
		assert_that ( exists ( "/tmp/dcterms.ttl" ), "Test file downloaded (dcterms)" ).is_true ()

	@staticmethod
	def test_overwrite ():
		if exists ( "/tmp/schema.ttl" ): os.remove ( "/tmp/schema.ttl" )
		dump_output ( lambda out: print ( "1", file = out ), "/tmp/schema.ttl" )
		
		download_file (
			"https://schema.org/version/latest/schemaorg-current-https.ttl", "/tmp/schema.ttl", "new schema.org", 
			overwrite = True
		)
		
		assert_that ( getsize ( "/tmp/schema.ttl" ) > 1000, "overwrite flag works" ).is_true ()

