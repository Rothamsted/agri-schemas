
"""
	Utilites about ETL pipelines, see the main package.
	
	:Authors: Marco Brandizi
	:Date: 2020
"""

from wsgiref import headers
from brandizpyes.ioutils import dump_output

from builtins import isinstance
import hashlib
import json
import logging.config
import os, io, csv
from os.path import dirname, abspath, isfile, exists
import string, re
from subprocess import run
from sys import stdout, stderr
import traceback
import urllib
import unittest
from typing import Generator, Any, Union



from pyparsing import ParseException
from rdflib import Graph
from rdflib.namespace import NamespaceManager
from rdflib.term import Literal
from rdflib.util import from_n3
import yaml

from functools import singledispatch
import shutil


"""
	Check that the environment variables expected by the ETL Tools is set. Raise an error
	if not.
"""
def check_env ():
	if not os.getenv ( "ETL_OUT" ):
		raise KeyError ( "ETL_OUT undefined, initialise the environment with some ***-env.sh" )

"""
	Check for the existence of the JENA_HOME environment variable. Raise an error if not found.
"""
def get_jena_home ():
	jena_home = os.getenv ( "JENA_HOME" )
	if not jena_home:
		raise KeyError ( "JENA_HOME not defined! Set it in your OS environment" )
	return jena_home

class XNamespaceManager ( NamespaceManager ):
	"""
		An extended version of rdflib.NamespaceManager, with a few little utilities added.
	"""
	
	def __init__ ( self, base_ns_mgr = None ):
		if not base_ns_mgr:
			base_ns_mgr = NamespaceManager( Graph () )
		self.__base = base_ns_mgr

	def __getattr__ ( self, attr ):
		"""
			Same as :meth:`__setattr__`.
		"""
		return getattr ( self.__base, attr )

	def __setattr__ ( self, attr, val ):
		"""
			Retains the ability to set namespaces as attributes.

			It just checks if the client is already accessing a base setter or ourselves and 
			dispatches accordingly.
		"""
		if attr == '_XNamespaceManager__base':
			NamespaceManager.__setattr__ ( self, attr, val )
		return setattr ( self.__base, attr, val )
	
	def uri_ref ( self, curie_or_prefix, tail = None ):
		"""
			Resolves a URI. 
			
			This might be either a CURIE using a known namespace prefix (eg, rdfs:label), 
			a namespace prefix followed by a tail (eg, "rdfs", "label"), or a namespace prefix 
			only (eg, "rdfs:").
			
			from_n3() is used, so the parameter could have other formats too (eg, <http://foo.com/ex>), 
			but the method isn't designed for that.
			
			This returns a rdflib's URIRef, use uri() to get a string.	
		"""
		curie = curie_or_prefix
		if tail: curie += ':' + tail
		return from_n3 ( curie, nsm = self )
	
	def uri ( self, curie_or_prefix, tail = None ) -> str:
		"""
			Invokes uri_ref() and translates the result into a string.
		"""
		return str ( self.uri_ref ( curie_or_prefix, tail ) )
	
	def ns_ref ( self, ns_prefix ):
		"""
			Returns the URI corresponding to a namespace prefix (as URIRef).
		"""
		if ns_prefix [-1] != ':': ns_prefix += ':'
		return self.uri_ref ( ns_prefix )

	def ns ( self, ns_prefix ) -> str:
		"""
			Invokes str(ns_ref())
		"""
		return str ( self.ns_ref ( ns_prefix ) )

	def to_lang ( self, line_template = 'PREFIX {prefix}: <{uri}>' ) -> str:
		"""
			Translates all the managed prefixes into a format suitable for an RDF language (eg, Turtle, SPARQL).
			
			Does this simply using a template like the default.
		"""
		nss = self.namespaces ()
		if not nss: return ""
		return '\n'.join ( [	line_template.format ( prefix = prefix, uri = uri ) for prefix, uri in nss ] )

	def to_sparql ( self ):
		"""
			See to_lang()
		"""
		return self.to_lang ()

	def to_turtle ( self ):
		"""
			See to_lang()
		"""
		return self.to_lang ( 'prefix {prefix}: <{uri}>' )

	def load ( self, doc_uri, rdf_format = None ):
		"""
			Loads namespace definitions from a file in formats like .ttl or .rdf. 
			Uses rdflib.Graph.parse().
		"""
		g = Graph ()
		g.parse ( doc_uri, format = rdf_format )
		self.merge_ns_manager ( g.namespace_manager )
	
	def merge_ns_manager ( self, nsm: NamespaceManager ):
		"""
			Merges another Namespace manager into this.
		"""
		for prefx, ns in nsm.namespaces ():
			self.bind ( prefx, ns, True, True )
	

DEFAULT_NAMESPACES = XNamespaceManager ()
"""
	These are loaded from various places:
		- /default-namespaces.ttl in this package
		- NAMESPACES_PATH if it is set
"""

DEFAULT_NAMESPACES.load ( 
	os.path.abspath ( 
		os.path.dirname ( __file__ ) + "/default-namespaces.ttl" 
	),
	"turtle"
)
if os.getenv ( 'NAMESPACES_PATH' ):
	DEFAULT_NAMESPACES.load ( os.getenv ( 'NAMESPACES_PATH' ), "turtle" )

"""
	An RDF test utility.

	Execute the ASK query against the graph and returns the result.
	
	if namespaces is None, nss to prefix ask_query are got from graph.namespace_manager
	if namespaces is explicitly False, no prefixes are added to the query 
"""
def sparql_ask ( graph: Graph, ask_query: str, namespaces = None ):
	if not namespaces and namespaces is not False:
		namespaces = XNamespaceManager ( graph.namespace_manager )
	if namespaces: 
		ask_query = namespaces.to_sparql () + "\n" + ask_query
	try:
		return bool ( graph.query ( ask_query ) )
	except ParseException as ex:
		raise ParseException ( "Error while executing SPARQL: '%s', query:\n%s" % ( ex.msg, ask_query ) ) from ex


"""
	WARNING! Never tested!
"""
def sparql_ask_tdb ( tdb_path: string, ask_query, namespaces = DEFAULT_NAMESPACES ):
	if namespaces: ask_query = namespaces.to_sparql () + "\n" + ask_query
	jena_home = get_jena_home ()
	proc = run ( 
		[ jena_home + "/bin/tdbquery", "--loc=%s" % tdb_path, "--query=-" ], 
		capture_output = True,
		input = ask_query,
		encoding = 'UTF-8'
	)
	if proc.returncode != 0:
		raise ChildProcessError ( "Error #%d while running ASK test " % proc.returncode )

	return "Yes" in proc.stdout

"""
	Gets an ID out of a string, by doing some normalisation.
	
	If skip_non_word_chars is set, non-words characters (\\W) are replaced with empty strings. This means
	that, for instance "aren't" and "arent" become the same ID. This might be useful when you build IDs
	out of free text, it's certainly isn't when you deal with stuff like accessions or preferred names.

	Note that characters like '/' and '.' are percent-encoded, to avoid syntax problems with RDF.
"""
def make_id ( s, skip_non_word_chars = False, ignore_case = True ):
	if ignore_case: s = s.lower ()
	s = re.sub ( "\\s", "_", s )
	s = re.sub ( "/", "%2F", s )
	s = re.sub ( "\\.", "%2E", s )
	if skip_non_word_chars: s = re.sub ( "\\W", "", s, flags = re.ASCII )
	s = urllib.parse.quote ( s )
	s = re.sub ( "%", "_0x", s, flags = re.ASCII ) # parsers don't like things like '%20'
	return s

def uri2accession ( uri ):
	"""
	Extracts the last part of a URI, relying on characters like '#' or '/'.
	"""
	bits = re.split ( "[\\/,\\#,\\?]", uri )
	if not bits: return ""
	return bits [ -1 ]

"""
	Computes a SHA1 hash from a string and returns a human-readable hexadecimal representation.
	
	This is often used to build unique identifiers from free-text strings. 
"""
def hash_string ( s: str, ignore_case = True ):
	if ignore_case: s = s.lower ()
	h = hashlib.sha1 ( s.encode() )
	return h.hexdigest()

"""
	Invokes hash_string from each str(element) in the generator.
	
	The stringified elements are sorted by default, so that two different lists always generate the same hash/ID.	
"""
def hash_generator ( g, ignore_case = True, sort = True ):
	l = [ str ( i ) for i in g ]
	if ignore_case: l = [ s.lower () for s in l ]
	if sort: l.sort()
	return hash_string ( "".join ( l ), ignore_case )

"""
	An adapter to send a string writer to a function that accepts a binary writer. 
	
	For instance, you can use this to write plain strings into a compressed file, 
	see details at https://stackoverflow.com/questions/66375185
	
	Usage example:
	
	with bz2.open ( file_path, "w" ) as bout
		out = BinaryWriter ( bout )
		print ( "Hello, world", file = out )
		my_output ( out ) # Uses print( ..., file = out )

				
	For cases where compression is optional:

	out = open ( file_path, mode = "w" ) if not file_path.endswith ( ".bz2" ) \
				else BinaryWriter ( bz2.open ( file_path, "w" ) )
	try:
		my_output ( out )
	finally:
		out.close ()
	
"""
class BinaryWriter:
	def __init__ ( self, bin_out, encoding = "utf-8", errors = 'strict' ):
		self.bin_out = bin_out
		self.encoding = encoding
		self.errors = errors
		
	def write ( self, s: str ):
		self.bin_out.write ( s.encode ( self.encoding, self.errors ) )

	def close ( self ):
		self.bin_out.close ()



"""
	Allows for some flexibility with CSV document reading.
	The rows_generator parameter can be either of:
	
	- an io.TextIOBase: passes it to csv.reader() and returns the resulting generator
	- a string: opens it as a file, calls itself recursively (to get a csv.reader()) and returns a generator
		that iterates over the csv rows like the previous case (done via yield, so the file is auto-closed)
	- anything else that supports 'yield': returns the corresponding generator
	- none of the above: raises an error
	
	As you see, it always returns a generator over which you can iterate independently on the initial source.	 
"""	
def normalize_rows_source ( rows_source ):
	if isinstance ( rows_source, str ):
		# Open the file with the csv reader
		with open ( rows_source ) as csvf:
			yield from normalize_rows_source ( csvf )
		return
	
	elif isinstance ( rows_source, io.TextIOBase ):
		# This includes stdin
		rows_source = csv.reader ( rows_source, delimiter = "\t" )

	yield from rows_source	


"""
	Utility to quickly send a row generator to an output of type string or file handle, as per
	dump_output()
"""
def dump_rows ( rows, out = stdout, mode = "w", **open_opts ):
	def writer ( out ):
		for row in rows:
			print ( row, file = out )
	dump_output ( out, writer, mode = mode, **open_opts )
		
def js_from_file ( file_path ):
	with open ( file_path ) as jsf:
		return json.load ( jsf )

def js_to_file ( js, file_path ):
	os.makedirs ( os.path.dirname ( file_path ), exist_ok = True )
	with open ( file_path, "w" ) as jsf:
		return json.dump ( js, jsf )
	

"""
	Returns an RDF/Turtle string if the key exists in the 'data' treated as dictionary.
	rdf_tpl must be a template like: dc:title "{title}", where 'title' is a data key 
	(usually the same as key) 
"""
def rdf_stmt ( data, key, rdf_tpl, rdf_val_provider = lambda v: v ):
	data = data.copy ()
	val = data.get ( key )
	if not val: return ""
	data [ key ] = rdf_val_provider ( val )
	return rdf_tpl.format ( **data )

"""
	The same as rdf_stmt(), but builds the RDF from an RDF property and a converter
"""
def rdf_pval ( data, key, rdf_prop, rdf_val_provider ):
	return rdf_stmt ( data, key, rdf_prop + " {" + key + "};\n", rdf_val_provider )

"""
	The same as rdf_pval(), for string values to be translated as literals.
"""
def rdf_str ( data, key, rdf_prop ):
	def lbuilder ( s ):
		return '"' + str ( Literal ( s ) ) + '"'
	return rdf_pval ( data, key, rdf_prop, lbuilder )

"""
	The same as rdf_str(), but the value is escaped into triple quotes
"""
def rdf_text ( data, key, rdf_prop ):
	def lbuilder ( s ):
		return '"""' + str ( Literal ( s ) ) + '"""'
	return rdf_pval ( data, key, rdf_prop, lbuilder )
	

"""
	Simple utility that wraps every line of the current traceback into a pair of prefixes/postfixes.
	
	This is useful to report errors in a data file that is later read by some other 
	data pipeline component. 

"""
def get_commented_traceback ( comment_prefix: str = "# ", comment_postfix: str = "" ):
	st = traceback.format_exc()
	st = st.splitlines ()
	st = [ comment_prefix + line + comment_postfix + "\n" for line in st ]
	return "".join ( st )


def download_file (
	url: str, out: str, label: str = None,
	accept_header: str = None, user_agent: str = None,
	out_dir: str = None, overwrite: bool = False
):
	"""
	Little helper to download a file from a URL to a local path.
	
	* :param url: source URL
	* :param out: output file path
	* :param label: Used to logging and alike
	* :param accept_header: if set, adds an HTTP Accept header to the request
	  This might be necessary for certain web servers
	* :param user_agent: if set, adds an HTTP User-Agent header to the request
		if it's None, it uses the default in urllib. We have experienced that DCMI doesn't like
		the latter
	* :param out_dir: base output directory, prefixed to 'out' if set
	* :param overwrite: if False, skips re-downloading for existing target files, else overwrites them

	"""
	log = logging.getLogger ( __name__ )
	if not label: label = out
	target_path = out
	if out_dir: target_path = out_dir + "/" + target_path
	if exists ( target_path ):
		if not isfile ( target_path ):
			raise ValueError ( f"Download target_path '{target_path}' exists but isn't a file" )
		if not overwrite: return

	log.info ( f"Downloading '{label}'" )

	# TODO: maybe we need to clarify why DCMI has decided that a machine-readable file cannot be downloaded
	# by a machine presenting itself as 'Python-urllib/X.YZ', letting apart what this annoyance is supposed 
	# to solve, when it can be so easily bypassed.
	headers = {}
	if user_agent is not None: headers [ "User-Agent" ] = user_agent
	if accept_header: headers [ 'Accept' ] = accept_header
	req = urllib.request.Request ( url, headers = headers )
	with urllib.request.urlopen ( req ) as response:
		with open ( target_path, "wb" ) as out:
			shutil.copyfileobj(response, out)


def download_files (
	generator: Generator[dict[str, Any]|list[Any], None, None], 
	out_dir: str = None, 
	overwrite: bool = False
):
	"""
	Downloads multiple files using download_file().

	The generator parameter allows for sending dictionaries of named parameters to
	:func:`download_file`, except for the common params being set here (which of course, are added to
	all the invocations).
	"""

	for item in generator:
		if out_dir: item [ "out_dir" ] = out_dir
		if overwrite: item [ "overwrite" ] = overwrite
		download_file ( **item )

"""
	TODO: comment me
"""
class XTestCase ( unittest.TestCase ):
	def assert_rdf ( self, graph, ask_query, fail_msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), fail_msg )		


if __name__ == '__main__':
	logger_config ()
	check_env ()
