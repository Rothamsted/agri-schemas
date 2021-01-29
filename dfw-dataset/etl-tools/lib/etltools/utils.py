import os, io, csv
from sys import stdout, stderr
from os.path import dirname, abspath
import string, re
import urllib
from rdflib import Graph
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3
from subprocess import run
from builtins import isinstance
import logging.config
import yaml


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
	s = re.sub ( "/", "%2F", s )
	if skip_non_word_chars: s = re.sub ( "\\W", "", s, re.ASCII )
	s = urllib.parse.quote ( s )
	s = re.sub ( "%", "_0x", s, re.ASCII ) # parsers don't like '%20'
	return s

"""
  Extract the last part of a URI, relyin on characters like '#' or '/'.
"""
def uri2accession ( uri ):
	bits = re.split ( "[\\/,\#,\?]", uri )
	if not bits: return ""
	return bits [ -1 ]



	
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

"""
  Utility to quickly deal with a writer that writes on a file handle.
  
  The function checks if out is an handle or a string, in case of string, interprets it as
  a file path, opens it and invokes writer() with the corresponding handle.
   
  If out is not a string, just invokes writer( out ), which, therefore, must get a file handle
  as parameter.
  
  mode and open_opts are parameters for the open() function. If out isn't a string, they're 
  ignored.  
"""
def dump_output ( out, writer, mode = "w", **open_opts):
	if isinstance ( out, str ):
		with open ( out, mode = mode, **open_opts ) as fout:
			return writer ( fout )
	return writer ( out )

"""
  Utility to quickly send a row generator to an output of type string or file handle, as per
  dump_output()
"""
def dump_rows ( rows, out = stdout, mode = "w", **open_opts ):
	def writer ( out ):
		for row in rows:
			print ( row, file = out )
	dump_output ( out, writer, mode = mode, **open_opts )
		

"""
  Configures the Python logging module with a YAML configuration file.
  
  The file name is picked from ETL_LOG_CONF, or from <current directory>/logging.yaml
  This should be called at the begin of a main program and BEFORE any use of the logging module.
  Multiple calls of this method are idempotent, ie, the Python logging module configures itself
  once only (and only before sending in logging messages).
  
  An example of logging config file is included in ETL tools.
  
  If logger_name is provided, the function returns logging.getLogger ( logger_name ) as a facility
  to avoid the need to import logging too, when you already import this. Beware that you load a configuration
  one only in your application (so, don't use this method in modules just to get a logger). 
  
  disable_existing_loggers is false by default, this is the best way to not interfere with modules instantiating
  their own module logger, usually before you call this function on top of your application (but usually after 
  all the imports). By default, the Python logging library has this otpion set to true and that typically causes
  all the module loggers to be disabled after the configuration loading. See https://docs.python.org/3/library/logging.config.html
"""
def logger_config ( logger_name = None, disable_existing_loggers = False ):
	cfg_path = os.getenv ( "ETL_LOG_CONF", "logging.yaml" )
	if not os.path.isfile ( cfg_path ):
		print ( "*** Logger config file '%s' not found, use the OS variable ETL_LOG_CONF to point to a logging configuration." % cfg_path, file = stderr )
		print ( "The logger will use the default configuration ", file = stderr )
		return
	with open ( cfg_path ) as flog:		
		cfg = yaml.load ( flog, Loader = yaml.FullLoader )
		# As per documentation, if not reset, this disables loggers in the modules, which usually are 
		# loaded during 'import', before calling this function
		cfg [ "disable_existing_loggers" ] = disable_existing_loggers
		logging.config.dictConfig ( cfg )
	log = logging.getLogger ( __name__ )
	log.info ( "Logger configuration loaded from '%s'" % cfg_path )

	if logger_name: return logging.getLogger ( logger_name )

if __name__ == '__main__':
	logger_config ()
	check_env ()

