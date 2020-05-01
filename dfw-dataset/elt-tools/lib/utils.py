import os, sys
from rdflib import Graph
from rdflib.namespace import NamespaceManager
from rdflib.util import from_n3


def check_elt_env ():
	if not os.getenv ( "ELT_OUT" ):
		print ( "\n\tERROR: ELT_OUT undefined, initialise the environment with some ***-env.sh\n" )
		sys.exit ( 1 )


class XNamespaceManager ( NamespaceManager ):
	def __init__ ( self, base_ns_mgr ):
		self.__base = base_ns_mgr

	def __getattr__ ( self, attr ):
		return getattr ( self.__base, attr )

	def __setattr__ ( self, attr, val ):
		if attr == '_XNamespaceManager__base':
			NamespaceManager.__setattr__ ( self, attr, val )
		return setattr ( self.__a, attr, val )
	
	def uri_ref ( self, curie_or_prefix, tail = None ):
		curie = curie_or_prefix
		if tail: curie += ':' + tail
		return from_n3 ( curie, nsm = self )
	
	def uri ( self, curie_or_prefix, tail = None ):
		return str ( self.uri ( curie_or_prefix, tail ) )
	
	def load ( self, doc_uri, format = None ):
		g = Graph ();
 		g.parse ( doc_uri, format )
 		self.merge_ns_mgr ( g.namespace_manager )
 	
 	def merge_ns_manager ( self, nsm ):
 		for prefx, ns in nsm.namespaces ():
 			self.bind ( prefx, ns, True, True )
 	
