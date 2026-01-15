import os
from os.path import dirname, abspath
from etltools.utils import sparql_ask, DEFAULT_NAMESPACES
import rdflib
import unittest
from zipfile import bz2

graph = None

def run_mappings ():
	global graph
	if graph: return
	graph = rdflib.Graph()

	mydir = dirname ( abspath ( __file__ ) )
	os.chdir ( mydir )
		
	print ( "Running mapping workflow" )
	if os.system ( "snakemake --verbose --snakefile sample-data-build.snakefile --cores all" ) != 0:
		raise ChildProcessError ( "Mapping workflow execution failed" )
	
	ETL_OUT = os.getenv ( "ETL_OUT" )
	DFW_ETL = os.getenv ( "DFW_ETL" )

	"""
		the bz2 can be used for verifications that need the original data, however, the tests 
		below are written against the output only, since these loadings are slow. 
	"""
	out_names = [
		# "knetminer-sample.ttl.bz2",
		"knetminer-mapping-test-out.nt"
	]
	for oname in out_names:
		out_path = ETL_OUT + "/test/" + oname
		print ( "--- Loading result from '%s'" % out_path )
		if oname.endswith ( ".bz2" ):
			with bz2.open ( out_path, mode = "rt" ) as fh:
				graph.parse ( source = fh )
			continue
		graph.parse ( out_path, format = "turtle" )	
	
	graph.parse ( DFW_ETL + "/../agri-schema.ttl", format = "turtle" )

	print ( "----- Test Initialised -----\n\n" )
	

class KnetSampleDataTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		run_mappings ()
		super().__init__ ( methodName )

	def assert_sparql ( self, ask_query, msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query, DEFAULT_NAMESPACES ), msg )

	def test_pref_name ( self ):
		for p in [ "rdfs:label", "schema:name", "skos:prefLabel" ]:
			self.assert_sparql (
				"ASK { bkr:trait_to_0006001 %s 'salt tolerance'}" % p,
				"%s not inferred!" % p
			)

	def test_name ( self ):
		s = "bkr:gene_at1g71100_locus_2026296"
		l = "ribose 5-phosphate isomerase"
		for p in [ "rdfs:label", "skos:altLabel" ]:
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
			"ASK { bkr:protein_p07519 a bioschema:Protein }",
			"bioschema:Protein not inferred!"
		)

	def test_bioschema_Publication ( self ):
		pmid = "3558409"
		
		for po in [ 
			"a agri:ScholarlyPublication", 
			"dcterms:title ?title",
			# "dcterms:identifier '%s'" % pmid, # TODO not in the sample dataset
			"dcterms:issued 1987",
			"schema:datePublished 1987"
		]:
			self.assert_sparql ( 
				"ASK { bkr:publication_%s %s }" % (pmid, po),
				"%s not inferred!" % ( po.split ( ' ' ) [ 0 ] )
			)
		
		self.assert_sparql ( 
			"""ASK { bkr:publication_%s 
			     schema:abstract ?abs;
			     dcterms:description ?abs 
			}""" % pmid,
			"abstract properties not inferred!" 
		)
		self.assert_sparql ( 
			"""ASK { bkr:publication_%s 
			     dcterms:creator ?authors;
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
			"ASK { bkr:gene_6652998 schema:isPartOf bkr:path_6645240 }",
			"schema:isPartOf not inferred!"
		)
		
	def test_agri_evidence ( self ):
		self.assert_sparql ( 
			"ASK { bkr:publication_28380544 agri:evidence bk:IMPD }",
			"agri:evidence not inferred!"
		)
		
	def test_dc_source ( self ):
		self.assert_sparql ( 
			"ASK { bkr:publication_12472693 dc:source bk:NLM_UNIPROTKB }",
			"dc:source not inferred!"
		)
	
	def test_mentions ( self ):
		self.assert_sparql ( 
			"""ASK { bkr:publication_22399647 
			     schema:mentions bkr:gene_bradi_3g39910v3, bkr:gene_horvu6hr1g085710
			}""",
			"schema:mentions not inferred!"
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
