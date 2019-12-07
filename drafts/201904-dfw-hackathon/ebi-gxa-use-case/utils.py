import re, csv 
from sys import stdin
import urllib.parse
from textwrap import dedent
from rdflib.term import Literal


""" 
	Gets an ID out of a string, by doing some normalisation
"""
def make_id ( s ):
	s = s.lower ()
	s = re.sub ( "\\s", "_", s )
	s = re.sub ( "\\W", "", s, re.ASCII )
	s = urllib.parse.quote ( s )
	return s

"""
	The organism-related GXA experiments fetched and re-processed manually from 
	https://www.ebi.ac.uk/gxa/experiments?species=arabidopsis%20thaliana&experimentType=baseline
"""
def get_gxa_accessions ():
	exp_accs = [ row [ 0 ] for row in csv.reader ( stdin, delimiter = "\t" ) ]
	exp_accs = [ re.sub ( "^https://www.ebi.ac.uk/gxa/experiments/", "", url ) for url in exp_accs ]
	return exp_accs

def print_rdf_namespaces ():
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
	print ( dedent ( rdf ) )

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
	The same, but builds the RDF from an RDF property and a converter
"""
def rdf_str ( data, key, rdf_prop ):
	def lbuilder ( s ): return '"' + str ( Literal ( s ) ) + '"'
	return rdf_pval ( data, key, rdf_prop, lbuilder )
