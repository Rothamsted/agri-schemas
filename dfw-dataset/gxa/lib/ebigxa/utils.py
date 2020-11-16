import types
from sys import stdin, stdout
import io
import urllib.parse
from textwrap import dedent
from rdflib.term import Literal


# The GXA-relevant namespaces
#
def rdf_gxa_namespaces ():
	rdf = """
		@prefix bkr: <http://knetminer.org/data/rdf/resources/> .
		@prefix agri: <http://agrischemas.org/> .
		@prefix bioschema: <http://bioschemas.org/> .
		@prefix schema: <http://schema.org/> .
		@prefix obo: <http://purl.obolibrary.org/obo/> .
		@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
		@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
		@prefix dc: <http://purl.org/dc/elements/1.1/> .
	"""
	return dedent ( rdf )

"""
	Returns an RDF/Turtle string, if the key exists in the data dictionary.
	rdf_tpl must be a template like: dc:title "{title}", where 'title' is a data key 
	(usually the same as key) 
"""
def rdf_stmt ( data, key, rdf_tpl, rdf_val_provider = lambda v: v ):
	data = data.copy ()
	val = data.get ( key )
	if not val: return ""
	# TODO: is this by copy?!
	data [ key ] = rdf_val_provider ( val )
	return rdf_tpl.format ( **data )

"""
	The same, but builds the RDF from an RDF property and a converter
"""
def rdf_pval ( data, key, rdf_prop, rdf_val_provider ):
	return rdf_stmt ( data, key, rdf_prop + " {" + key + "};\n", rdf_val_provider )

"""
	The same, for string values to be translated as literals.
"""
def rdf_str ( data, key, rdf_prop ):
	def lbuilder ( s ): return '"' + str ( Literal ( s ) ) + '"'
	return rdf_pval ( data, key, rdf_prop, lbuilder )


