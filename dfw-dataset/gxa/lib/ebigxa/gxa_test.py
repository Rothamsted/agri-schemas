import unittest
import io
from ebigxa.gxa import rdf_gxa_conditions, rdf_gxa_tpm_levels
from etltools.utils import logger_config, sparql_ask
import rdflib

log = logger_config ( __name__ )


class GxaTest ( unittest.TestCase ):

	def test_gxa_conditions ( self ):
		cond_labels = [ 'pericarp', 'Seed growth', '10 days after anthesis' ]
		out = io.StringIO ()
		rdf_gxa_conditions ( cond_labels, out )
		outs = out.getvalue ()
		log.info ( "rdf_gxa_conditions() test output:\n%s", outs )
		
		probes = [
			( "bkr:cond_pericarp dc:type <http://aims.fao.org/aos/agrovoc/c_25199>.", 
			  "Cannot find agrovoc:c_25199 for pericarp!" ),
			( "<http://aims.fao.org/aos/agrovoc/c_25199> schema:name \"pericarp\".", 
				"Cannot find schema:name for pericarp!" ),
			( "<http://purl.obolibrary.org/obo/PO_0009084> schema:identifier \"PO_0009084\".", 
			  "Cannot find schema:name for pericarp!"),
			(	"<http://knetminer.org/data/rdf/resources/plantontologyterm_po_0009010> schema:sameAs <http://purl.obolibrary.org/obo/PO_0009010>." in outs, 
				"Cannot fine knetminer/PO sameAs annotation for PO:0009010" ),
			( "bkr:cond_10_days_after_anthesis dc:type <http://aims.fao.org/aos/agrovoc/c_2992>.",
			 	"Cannot find 'flowering' annotation for anthesis entry" ),
			( "bkr:cond_10_days_after_anthesis dc:type <http://www.cropontology.org/rdf/CO_330:0000155>.",
				"Cannot find 'days' annotation for anthesis entry")
		]
		
		for (rdf, msg) in probes:
			self.assertTrue ( rdf, msg )


	def test_rdf_gxa_tpm_levels ( self ):
		accs = [ "E-MTAB-4484" ]
		gene_filter = [ "TRAESCS3D02G284900", "TRAESCS7B02G271500", "TRAESCS7D02G366600", "TRAESCS7B02G271600", 
										"TRAESCS3B02G319000", "TRAESCS7D02G366500", "TRAESCS7A02G356200", "TRAESCS7A02G356100" ]
		out = io.StringIO ()
		cond_labels = rdf_gxa_tpm_levels ( accs, out, gene_filter )
		outs = out.getvalue ()
		log.info ( "rdf_gxa_tpm_levels() test output (truncated):\n%s\n\n", outs [ 0: 4000 ] )		
		log.info ( "rdf_gxa_tpm_levels(), returned conditions: %s", cond_labels )
		
		graph = rdflib.Graph()
		graph.parse ( data = outs, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs7a02g356100 a bioschema:Gene }",
			"Test gene TRAESCS7A02G356100 not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs7a02g356100 schema:identifier 'TRAESCS7A02G356100' }",
			"TRAESCS7A02G356100 identifier not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf a rdfs:Statement }",
			"traescs7a02g356100/stage-30-50 not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf agri:tpmCount 17.0 }",
			"traescs7a02g356100/stage-30-50 without TPM count!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf agri:tpmCount 17.0 }",
			"traescs7a02g356100/stage-30-50 wrong or no TPM count!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf agri:ordinalTpm 'medium' }",
			"traescs7a02g356100/stage-30-50 wrong or no ordinal TPM!"
		)

		self.assert_rdf ( graph, 
			"""ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf
								rdf:subject bkr:gene_traescs7a02g356100;
								rdf:predicate bioschema:expressedIn;
								rdf:object bkr:cond_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf;
								agri:evidence bkr:exp_E-MTAB-4484. }""",
			"traescs7a02g356100/stage-30-50 wrong statements!"
		)

		self.assertTrue (
			"whole plant fruit formation stage 30 to 50%, leaf" in cond_labels,
			"Condition not in the result!"
		)

	
	def assert_rdf ( self, graph, ask_query, fail_msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), fail_msg )		

		

		
if __name__ == '__main__':
	unittest.main()