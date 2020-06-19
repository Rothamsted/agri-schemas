import os, sys
from os.path import dirname, abspath
from etltools import sparulmap
from etltools.utils import get_jena_home, sparql_ask
import rdflib
import unittest

graph = None

def run_mappings ():
	global graph
	if graph: return
	graph = rdflib.Graph()

	mydir = dirname ( abspath ( __file__ ) )
	os.chdir ( mydir )
		
	print ( "Running mapping workflow" )
	if os.system ( "snakemake --snakefile sample-data-build.snakefile --configfile ../../snake-config.yaml" ) != 0:
		raise ChildProcessError ( "Mapping workflow execution failed" )
	
	ETL_OUT = os.getenv ( "ETL_OUT" )
	out_names = [
		"knetminer-mapping-test-out.ttl",
		"knetminer-sample.ttl"
	]
	for oname in out_names:
		out_path = ETL_OUT + "/test/" + oname
		print ( "--- Loading result from '%s'" % out_path )
		graph.parse ( out_path, format = "turtle" )	

	print ( "----- Test Initialised -----\n\n" )
	

class KnetSampleDataTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		run_mappings ()
		super().__init__ ( methodName )

	def assert_sparql ( self, ask_query, msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), msg )

	def test_pref_name ( self ):
		for p in [ "rdfs:label", "bk:name", "schema:name", "skos:prefLabel" ]:
			self.assert_sparql (
				"ASK { bkr:to_0002682 %s 'plant cell shape'}" % p,
				"%s not inferred!" % p
			)

	def test_name ( self ):
		s = "bkr:to_0000387"
		l = "plant phenotype"
		for p in [ "rdfs:label", "bk:name", "skos:altLabel" ]:
			self.assert_sparql (
				"ASK { %s %s '%s'}" % (s, p, l),
				"%s not inferred!" % p
			)
		for p in [ "schema:name", "skos:prefLabel" ]:
			self.assert_sparql (
				"ASK { FILTER NOT EXISTS { %s %s '%s' } }" % (s, p, l),
				"%s wrongly inferred!" % p
			)
	
	def test_bioschema_Protein ( self ):
		self.assert_sparql ( 
			"ASK { bkr:protein_q0d6f4 a bioschema:Protein }",
			"bioschema:Protein not inferred!"
		)

	def test_bioschema_Publication ( self ):
		pmid = "18089549"
		
		for po in [ 
			"a agri:ScholarlyPublication", 
			"dcterms:title 'The Rice Annotation Project Database (RAP-DB): 2008 update.'",
			"dcterms:identifier '%s'" % pmid,
			"dcterms:issued 2008",
			"schema:datePublished 2008"
		]:
			self.assert_sparql ( 
				"ASK { bkr:publication_%s %s }" % (pmid, po),
				"%s not inferred!" % ( po.split ( ' ' ) [ 0 ] )
			)
		
		self.assert_sparql ( 
			"""ASK { bkr:publication_%s 
			     bka:Abstract ?abs;
			     schema:abstract ?abs;
			     dcterms:description ?abs 
			}""" % pmid,
			"abstract properties not inferred!" 
		)
		self.assert_sparql ( 
			"""ASK { bkr:publication_%s 
			     bka:AUTHORS ?authors;
			     dc:creator ?authors;
			     agri:authorsList ?authors 
			}""" % pmid,
			"author properties not inferred!" 
		)
		
	""" 
		Test that a bug about schema is fixed by our own special rules.
	"""
	def test_name_is_not_title ( self ):
		self.assert_sparql ( 
			"ASK { FILTER NOT EXISTS { ?s schema:name ?name; dcterms:title ?name } }", 
			"" 
		)
		

	def test_bioschema_isPartOf ( self ):
		self.assert_sparql ( 
			"ASK { bkr:to_0000804 schema:isPartOf bkr:to_0006031 }",
			"schema:isPartOf not inferred!"
		)
		self.assert_sparql ( 
			"ASK { bkr:to_0006031 schema:hasPart bkr:to_0000804 }",
			"schema:hasPart not inferred!"
		)
		
	def test_agri_evidence ( self ):
		self.assert_sparql ( 
			"ASK { bkr:publication_16240171 agri:evidence bk:IMPD }",
			"agri:evidence not inferred!"
		)
		
	def test_dc_source ( self ):
		self.assert_sparql ( 
			"ASK { bkr:publication_16240171 dc:source bk:NLM_UNIPROTKB }",
			"dc:source not inferred!"
		)
	
	def test_mentions ( self ):
		self.assert_sparql ( 
			"""ASK { bkr:publication_16240171 
			     schema:mentions bkr:protein_q6zgp8, bkr:protein_q75wv3
			}""",
			"dc:source not inferred!"
		)

"""
  TODO: 
	rdf:Statement & co (including agri:score/bka:TFIDF, accessions, 
	bioschema:expressedIn
	properties linking ontology terms
	ontology use case
"""

if __name__ == '__main__':
	unittest.main()
