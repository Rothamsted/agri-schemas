import unittest
from ebigxa.gxa import gxa_get_experiment_descriptors, rdf_gxa_conditions, rdf_gxa_tpm_levels, \
	load_filtered_genes, rdf_gxa_dex_levels, gxa_rdf_all
from ebigxa.utils import rdf_gxa_namespaces
from etltools.utils import logger_config, js_from_file, sparql_ask, XTestCase
import rdflib
import os

log = logger_config ( __name__ )
mod_dir_path = os.path.dirname ( os.path.abspath ( __file__ ) )


class GxaTestRaw ( XTestCase ):
	def test_gxa_rdf_all ( self ):
		exp_js = js_from_file ( mod_dir_path + "/test-data/E-ATMX-20.biostudies.json" )
		rdf = gxa_rdf_all ( exp_js, None )
		#log.info ( "gxa_rdf_all() test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )
		log.info ( "gxa_rdf_all() test output (truncated):\n%s\n\n", rdf )

		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )


class GxaTest: # TODO: restore ASAP ( XTestCase ):
	
	gxa_exps = None
	gene_filter = None
	
	@classmethod
	def setUpClass(cls):
		GxaTest.gene_filter = load_filtered_genes ( 
			[ "TRAESCS3D02G284900", "TRAESCS7B02G271500", "TRAESCS7D02G366600", "TRAESCS7B02G271600", 
				"TRAESCS3B02G319000", "TRAESCS7D02G366500", "TRAESCS7A02G356200", "TRAESCS7A02G356100",
				"TraesCS1A02G115900", "AT1G01010", "AT1G01030", "AT1G01040", "AT1G01070", "AT1G01080", 
				"AT1G01110", "AT1G01120", "AT1G01130", "AT1G01140", "AT1G01190", "AT1G01220", "AT1G01225", 
				"AT1G01250", "AT1G01290", "AT1G01320", "AT1G01360", "AT1G01390", "AT1G01420", "AT1G01470", 
				"AT1G01480", "AT1G01560", "AT4G03210", "AT4G30280", "AT5G59710", "AT1G22810", "AT3G30720",
				"ENSRNA050013890" ])
		GxaTest.gxa_exps = gxa_get_experiment_descriptors ( [ "arabidopsis thaliana", "triticum aestivum" ] ) 
		#log.info ( gxa_exps )
	
	# TODO: Agroportal isn't so stable
	def test_gxa_conditions ( self ):
		cond_labels = [ 'pericarp', 'Seed growth', '10 days after anthesis', '24 hours' ]
		rdf = rdf_gxa_namespaces()
		rdf += rdf_gxa_conditions ( cond_labels, None )
		log.info ( "rdf_gxa_conditions() test output:\n%s", rdf )
		
		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		probes = [
			( "bkr:cond_pericarp a agri:StudyFactor; schema:name 'pericarp'", 
			  "Cannot find RDF for pericarp!" ),
			( "bkr:cond_seed_growth a agri:StudyFactor; schema:name 'Seed growth'", 
			  "Cannot find RDF for seed growth!" ),
			( "bkr:cond_10_days_after_anthesis a agri:StudyFactor; schema:name '10 days after anthesis'", 
			  "Cannot find RDF for 10 days after anthesis!" ),
			( "bkr:cond_pericarp dc:type <http://aims.fao.org/aos/agrovoc/c_25199>", 
			  "Cannot find agrovoc:c_25199 for pericarp!" ),
			( "<http://aims.fao.org/aos/agrovoc/c_25199> schema:name \"pericarp\"", 
				"Cannot find schema:name for pericarp!" ),
			( "<http://purl.obolibrary.org/obo/PO_0009084> schema:identifier \"PO_0009084\"", 
			  "Cannot find schema:name for pericarp!"),
			(	"<http://knetminer.org/data/rdf/resources/plantontologyterm_po_0009010> schema:sameAs <http://purl.obolibrary.org/obo/PO_0009010>", 
				"Cannot fine knetminer/PO sameAs annotation for PO:0009010!" ),
			( "bkr:cond_10_days_after_anthesis dc:type <http://aims.fao.org/aos/agrovoc/c_2992>",
			 	"Cannot find 'flowering' annotation for anthesis entry!" ),
			( "bkr:cond_10_days_after_anthesis dc:type <http://www.cropontology.org/rdf/CO_330:0000155>",
				"Cannot find 'days' annotation for anthesis entry!"),
			( """
					bkr:cond_24_hours a agri:StudyFactor;
						schema:name "24 hours";
						schema:value 24;
						schema:unitText "hours"
					.
				""",
				"Cannot find right annotations about the 24 hours time point!"
			)
		]
		
		for (rdf, msg) in probes:
			self.assert_rdf ( graph, "ASK { %s }" % rdf, msg )
	
	
	def test_gxa_get_experiment_descriptors ( self ):
		self.assertTrue ( "E-MTAB-8326" in GxaTest.gxa_exps, "Arabidopsis experiment not found!" )
		self.assertEqual ( 
			"Differential", 
			GxaTest.gxa_exps [ "E-MTAB-8326" ] [ "gxaAnalysisType" ],
			"Wrong gxaAnalysisType for ara. experiment!"
		) 
		self.assertEqual ( 
			"Baseline", 
			GxaTest.gxa_exps [ "E-MTAB-4260" ] [ "gxaAnalysisType" ],
			"Wrong gxaAnalysisType for wheat experiment!"
		) 
		
		
	def test_rdf_gxa_tpm_levels ( self ):
		cond_labels = set()
		rdf = rdf_gxa_namespaces();
		rdf += rdf_gxa_tpm_levels ( "E-MTAB-4484", None, cond_labels, GxaTest.gene_filter )
		
		log.info ( "rdf_gxa_tpm_levels() test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )		
		log.info ( "rdf_gxa_tpm_levels(), returned conditions: %s", cond_labels )
		
		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs7a02g356100 a bioschema:Gene }",
			"Test gene TRAESCS7A02G356100 not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs7a02g356100 schema:identifier 'TRAESCS7A02G356100' }",
			"TRAESCS7A02G356100 identifier not stated!"
		)
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs1a02g115900 rdfs:label 'ALI1'. }",
			"traescs1a02g115900 rdfs:label not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4484_traescs7a02g356100_whole_plant_fruit_formation_stage_30_to_50_0x25_0x2C_leaf a rdf:Statement }",
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
		
		
	def test_rdf_gxa_dex_levels ( self ):
		cond_labels = set()
		rdf = rdf_gxa_namespaces();
		rdf += rdf_gxa_dex_levels ( "E-MTAB-4289", "RNASeq", None, cond_labels, GxaTest.gene_filter )
		
		log.info ( "rdf_gxa_dex_levels() test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )		
		log.info ( "rdf_gxa_dex_levels(), returned conditions: %s", cond_labels )
		
		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_ensrna050013890 a bioschema:Gene }",
			"Test gene ENSRNA050013890 not stated!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:gene_ensrna050013890 schema:identifier 'ENSRNA050013890' }",
			"ENSRNA050013890 identifier not stated!"
		)
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_ensrna050013890 rdfs:label 'LSU_rRNA_eukarya'. }",
			"ENSRNA050013890 rdfs:label not stated!"
		)
		
		cond_uri = "bkr:gxaexp_E-MTAB-4289_traescs7d02g366500_blumeria_graminis_0x3B_72_hour_vs_control"
		self.assert_rdf ( graph, 
			f"""ASK {{ {cond_uri} a rdf:Statement; 
				rdf:subject bkr:gene_traescs7d02g366500;
				rdf:predicate bioschema:expressedIn;
				rdf:object bkr:cond_blumeria_graminis_0x3B_72_hour;
			}}""",
			f"{cond_uri} not stated!"
		)
		self.assert_rdf ( graph, 
			"ASK { bkr:gene_traescs7d02g366500 bioschema:expressedIn bkr:cond_blumeria_graminis_0x3B_72_hour. }",
			f"{cond_uri} not stated (summary statement)!"
		)
		
		self.assert_rdf ( graph, 
			f"ASK {{ {cond_uri} agri:log2FoldChange 2.2 }}", f"{cond_uri}'s fold-change not stated!"
		)
		
		self.assert_rdf ( graph, 
			f"""ASK {{ {cond_uri} agri:pvalue ?pvalue.
				         FILTER ( ?pvalue < 0.05 ) }}""",
			f"{cond_uri}'s pvalue not stated or bad pvalue!"
		)
		
		self.assert_rdf ( graph, 
			f"ASK {{ {cond_uri} agri:evidence bkr:exp_E-MTAB-4289 }}", f"{cond_uri}'s evidence not stated!"
		)

		self.assert_rdf ( graph, 
			f"ASK {{ {cond_uri} agri:baseCondition bkr:cond_control }}", f"{cond_uri}'s base condition not stated!"
		)
				
		self.assertEqual ( 
			set ( [ 'control', 'Blumeria graminis; 24 hour', 'Blumeria graminis; 72 hour' ] ), cond_labels,
			"Wrong set of conditions returned!"
		)
		
		
	def test_rdf_gxa_dex_levels_microarray ( self ):
		cond_labels = set()
		rdf = rdf_gxa_namespaces();
		rdf += rdf_gxa_dex_levels ( "E-MTAB-8326", "Microarray", None, cond_labels, GxaTest.gene_filter )
		
		log.info ( "rdf_gxa_dex_levels(Microarray) test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )		
		log.info ( "rdf_gxa_dex_levels(Microarray), returned conditions: %s", cond_labels )
		
		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )		
		
		self.assert_rdf ( graph, 
		  """ASK { 
		    ?dex a rdf:Statement;
					rdf:subject ?gene;
					rdf:predicate bioschema:expressedIn;
					rdf:object bkr:cond_vip2_overexpression;
					agri:baseCondition bkr:cond_wild_type_genotype;
					agri:log2FoldChange ?fc;
					agri:pvalue ?pvalue;
					agri:evidence bkr:exp_E-MTAB-8326;
					agri:timePoint bkr:cond_0_hours
				.
					
				FILTER ( ?pvalue < 0.05 )
				FILTER ( ABS( ?fc ) > 1 )
				
				?gene a bioschema:Gene;
					schema:identifier "AT1G01010";
					rdfs:label "NAC001"
				.   
		  }""",
		  "DEX statements about 0 hrs not found!"								
		)
		
		self.assert_rdf ( graph, 
		  """ASK { 
		    ?dex a rdf:Statement;
					rdf:subject ?gene;
					rdf:predicate bioschema:expressedIn;
					rdf:object ?cond;
					agri:baseCondition ?baseline;
					agri:log2FoldChange ?fc;
					agri:pvalue ?pvalue;
					agri:evidence bkr:exp_E-MTAB-8326;
					agri:timePoint bkr:cond_72_hours
				.
					
				FILTER ( ?pvalue < 0.05 )
				FILTER ( ABS( ?fc ) > 1 )
		  }""",
		  "DEX statements about 72 hrs not found!"								
		)		
		
	
	def test_extended_baseline ( self ):
		cond_labels = set()
		rdf = rdf_gxa_namespaces();
		rdf += rdf_gxa_dex_levels ( "E-MTAB-8073", "RNASeq", None, cond_labels, GxaTest.gene_filter )
		
		log.info ( "rdf_gxa_dex_levels(Microarray) test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )		
		log.info ( "rdf_gxa_dex_levels(Microarray), returned conditions: %s", cond_labels )
		
		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )	
		
		self.assert_rdf ( graph, 
		  """ASK { 
		    ?dex a rdf:Statement;
					rdf:subject ?gene;
					rdf:predicate bioschema:expressedIn;
					rdf:object bkr:cond_sodium_chloride_0x3B_150_millimolar;
					agri:baseCondition bkr:cond_none, bkr:cond_wild_type_genotype;
					agri:log2FoldChange ?fc;
					agri:pvalue ?pvalue;
					agri:evidence bkr:exp_E-MTAB-8073;
				.
					
				FILTER ( ?pvalue < 0.05 )
				FILTER ( ABS( ?fc ) > 1 )
				
				
		  }""",
		  "DEX statements about sodium_chloride not found!"								
		)		
				
		self.assertTrue( "wild type genotype" in cond_labels, "Extended base condition in DEX experiment not found!" )
		
		
	def test_gxa_rdf_all ( self ):
		acc = "E-MTAB-4260"
		exp_js = GxaTest.gxa_exps [ acc ]
		
		rdf = gxa_rdf_all ( exp_js, out = None, target_gene_ids = GxaTest.gene_filter )
		log.info ( "gxa_rdf_all() test output (truncated):\n%s\n\n", rdf )		

		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"ASK { bkr:exp_E-MTAB-4260 a bioschema:Study }",
			"No Study RDF!"
		)
		
		self.assert_rdf ( graph, 
			"ASK { bkr:gxaexp_E-MTAB-4260_traescs1a02g115900_endosperm_and_seed_coat_0x2C_4_days_after_pollination a rdf:Statement }",
			"Gene expression statement not found!"
		)

		self.assert_rdf ( graph, 
			"""ASK { bkr:cond_pericarp_0x2C_12_days_after_pollination a agri:StudyFactor;
							   schema:name "pericarp, 12 days after pollination" }""",
			"Condition's RDF not found!"
		)

		self.assert_rdf ( graph, 
			"ASK { bkr:cond_pericarp_0x2C_12_days_after_pollination dc:type <http://aims.fao.org/aos/agrovoc/c_25199> }",
			"Condition's ontology annotations not found!"
		)
# /ens:GxaTest		

		
if __name__ == '__main__':
	unittest.main()