import os, io, csv
import types
from collections.abc import Iterable, Iterator   
from os.path import dirname, abspath
import string, re
import urllib
from rdflib import Graph
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3
from subprocess import run
from builtins import isinstance

def check_env ():
	if not os.getenv ( "ETL_OUT" ):
		raise KeyError ( "ETL_OUT undefined, initialise the environment with some ***-env.sh" )

def get_jena_home ():
	jena_home = os.getenv ( "JENA_HOME" )
	if not jena_home:
		raise KeyError ( "JENA_HOME not defined! Set it in your OS environment" )
	return jena_home


class XNamespaceManager ( NamespaceManager ):
	
	def __init__ ( self, base_ns_mgr = None ):
		if not base_ns_mgr:
			base_ns_mgr = NamespaceManager( Graph () )
		self.__base = base_ns_mgr

	def __getattr__ ( self, attr ):
		return getattr ( self.__base, attr )
 
	def __setattr__ ( self, attr, val ):
		if attr == '_XNamespaceManager__base':
			NamespaceManager.__setattr__ ( self, attr, val )
		return setattr ( self.__base, attr, val )
	
	def uri_ref ( self, curie_or_prefix, tail = None ):
		curie = curie_or_prefix
		if tail: curie += ':' + tail
		return from_n3 ( curie, nsm = self )
	
	def uri ( self, curie_or_prefix, tail = None ):
		return str ( self.uri_ref ( curie_or_prefix, tail ) )
	
	def ns_ref ( self, ns_prefix ):
		if ns_prefix [-1] != ':': ns_prefix += ':'
		return self.uri_ref ( ns_prefix )

	def ns ( self, ns_prefix ):
		return str ( self.ns_ref ( ns_prefix ) )

	def to_lang ( self, line_template = 'PREFIX {prefix}: <{uri}>' ):
		nss = self.namespaces ()
		if not nss: return ""
		return '\n'.join ( [  line_template.format ( prefix = prefix, uri = uri ) for prefix, uri in nss ] )

	def to_sparql ( self ):
	  return self.to_lang ()

	def to_turtle ( self ):
	  return self.to_lang ( 'prefix {prefix}: <{uri}>' )

	def load ( self, doc_uri, format = None ):
		g = Graph ()
		g.parse ( doc_uri, format = format )
		self.merge_ns_manager ( g.namespace_manager )
 	
	def merge_ns_manager ( self, nsm ):
		for prefx, ns in nsm.namespaces ():
			self.bind ( prefx, ns, True, True )
 	

DEFAULT_NAMESPACES = XNamespaceManager ()
DEFAULT_NAMESPACES.load ( dirname ( abspath ( __file__ ) ) + "/default-namespaces.ttl", "turtle" )
if os.getenv ( 'NAMESPACES_PATH' ):
	DEFAULT_NAMESPACES.load ( os.getenv ( 'NAMESPACES_PATH' ), "turtle" )


def sparql_ask ( graph: Graph, ask_query, namespaces = DEFAULT_NAMESPACES ):
	if namespaces: ask_query = namespaces.to_sparql () + "\n" + ask_query
	return bool ( graph.query ( ask_query ) )


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
	
	If skip_non_word_chars is set, non-words characters (\W) are replaced with empty strings. This means
	that, for instance "aren't" and "arent" become the same ID. This might be useful when you build IDs
	out of free text, it's certainly isn't when you deal with stuff like accessions or preferred names. 
"""
def make_id ( s, skip_non_word_chars = False ):
	s = s.lower ()
	s = re.sub ( "\\s", "_", s )
	if skip_non_word_chars: s = re.sub ( "\\W", "", s, re.ASCII )
	s = urllib.parse.quote ( s )
	return s

	
"""
	Allows for some flexibility with CSV document reading.
	The rows_generator parameter can be either of:
	
	- an io.TextIOBase: passes it to csv.reader() and returns the resulting generator
	- a string: opens it as a file, calls itself recursively (to get a csv.reader()) and returns a generator
	  that iterates over the csv rows like the previous case (done via yield, so the file is auto-closed)
	- anything else that supports 'yield': returns the corresponding generator
	- none of the above: raise an error
	
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

if __name__ == '__main__':
	check_env ()
