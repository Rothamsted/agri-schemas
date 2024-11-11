import unittest
from etltools.utils import logger_config, sparql_ask, js_from_file, XTestCase
from ebigxa.ae import ae_get_experiment_accessions, rdf_ae_experiment
from ebigxa.utils import rdf_gxa_namespaces
import rdflib
import os

log = logger_config ( __name__ )
mod_dir_path = os.path.dirname ( os.path.abspath ( __file__ ) )

"""
	TODO: comment me!
"""
class AeTestRaw ( XTestCase ):
	def test_rdf_ae_experiment_microarray ( self ):
		exp_js = js_from_file ( mod_dir_path + "/test-data/E-ATMX-20.biostudies.json" )
		rdf = rdf_gxa_namespaces()		
		rdf += rdf_ae_experiment ( exp_js, None )
		log.info ( "rdf_ae_experiment() test output:\n%s\n\n", rdf )

		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"""ASK {
			  bkr:exp_E-ATMX-20 a bioschema:Study;
					schema:identifier "E-ATMX-20";
					dc:title ?title;
					schema:description ?descr;
					schema:datePublished "2008-02-05".
				
				FILTER ( REGEX ( ?title, "Transcription profiling wild type and Zat10" ) )
				FILTER ( REGEX ( ?descr, "The effect of overexpression of Zat10 in Arabidopsis" ) )
			}""", 
			"Basic RDF data about E-ATMX-20 not found!"
		)

		self.assert_rdf ( graph,
			"""ASK {
				bkr:exp_E-ATMX-20 bioschema:studyProcess ?design.

				?design a agri:ExperimentalDesign, schema:PropertyValue;
					schema:name "study design";
					schema:propertyID ppeo:experimental_design;
					dc:type <http://purl.obolibrary.org/obo/OBI_0500014>;				
					schema:description "Factorial design, technology: Transcription profiling by array, analysis type: Differential.";
					schema:additionalProperty bkr:ae_technology_type_microarray, bkr:gxa_analysis_type_differential.
			}
			""",
			"Study design annotations not found for E-ATMX-20!"
		)
	# /end: test_rdf_ae_experiment_microarray ()

	def test_rdf_ae_experiment_sequencing ( self ):
		exp_js = js_from_file ( mod_dir_path + "/test-data/E-MTAB-4484.biostudies.json" )
		rdf = rdf_gxa_namespaces()		
		rdf += rdf_ae_experiment ( exp_js, None )
		log.info ( "rdf_ae_experiment() test output:\n%s\n\n", rdf )

		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph,
			"""ASK {
				bkr:exp_E-MTAB-4484 bioschema:studyProcess ?design.

				?design a agri:ExperimentalDesign, schema:PropertyValue;
					schema:name "study design";
					schema:propertyID ppeo:experimental_design;
					dc:type <http://purl.obolibrary.org/obo/OBI_0500014>;				
					schema:description "Factorial design, technology: RNA-seq of coding RNA, analysis type: Baseline.";
					schema:additionalProperty bkr:ae_technology_type_rna_sequencing, bkr:gxa_analysis_type_baseline.
			}
			""",
			"Study design annotations not found for E-MTAB-4484!"
		)
	# /end: test_rdf_ae_experiment_sequencing ()	
# /end: AeTestRaw


class AeTest ( XTestCase ):	
	ae_exps = None
	
	@classmethod
	def setUpClass(cls):
		AeTest.ae_exps = ae_get_experiment_accessions ( [ "Arabidopsis thaliana", "Triticum aestivum" ] ) 
		#log.info ( "EXPS:\n%s", ae_exps ) 
		
	def test_ae_accessions ( self ):
		self.assertTrue ( "E-MTAB-9838" in AeTest.ae_exps, "Arabidopsis experiment not found!" )
		self.assertTrue ( "E-GEOD-25759" in AeTest.ae_exps, "Wheat experiment not found!" )
		self.assertTrue ( "E-MEXP-254" in AeTest.ae_exps, "page 6 experiment not found!" )
		
	def test_rdf_ae_experiments ( self ):
		return # TODO: restore
		rdf = rdf_gxa_namespaces()		
		rdf += rdf_ae_experiment ( AeTest.ae_exps [ 'E-MTAB-8326' ], None )
		rdf += rdf_ae_experiment ( AeTest.ae_exps [ 'E-GEOD-25759' ], None )
		log.info ( "rdf_ae_experiment() test output (truncated):\n%s\n\n", rdf [ 0: 4000 ] )

		graph = rdflib.Graph()
		graph.parse ( data = rdf, format = "turtle" )
		
		self.assert_rdf ( graph, 
			"""ASK {
			  bkr:exp_E-MTAB-8326 a bioschema:Study;
					schema:identifier "E-MTAB-8326";
					dc:title ?title;
					schema:description ?descr;
					schema:datePublished "2019-09-26";
					# We can't test gxaAnalysisType here, cause that's added by gxa_get_experiment_descriptor ()
					# so we test it in gxa_test
					schema:additionalProperty bkr:ae_technology_type_microarray.	
				
				FILTER ( REGEX ( ?title, "Transcriptome analysis of Arabidopsis VIRE2-INTERACTING PROTEIN2" ) )
				FILTER ( REGEX ( ?descr, "C-terminal NOT2 domain of VIP2 interacts with VirE2" ) )
			}""", 
			"Basic RDF data about E-MTAB-8326 not found!"
		)
		
		self.assert_rdf ( graph, 
			"""ASK {
				bkr:exp_E-GEOD-25759 schema:additionalProperty bkr:specie_triticum_aestivum.
				bkr:specie_triticum_aestivum a schema:PropertyValue;
					schema:propertyID "organism";
					schema:value "Triticum aestivum".
			}""", 
			"Specie RDF data about E-GEOD-25759 not found!"
		)		

		self.assert_rdf ( graph, 
			"""ASK {
				bkr:exp_E-GEOD-25759 schema:subjectOf bkr:pmid_21981858.
				bkr:pmid_21981858 a agri:ScholarlyPublication;
					dc:title ?title; 
					agri:authorsList ?authors;
					agri:pmedId "21981858"
				.
				
				FILTER ( REGEX ( ?title, "Effect of the down-regulation of the high Grain Protein Content" ) )
				FILTER ( REGEX ( ?authors, "Cantu D, Pearce SP, Distelfeld A" ) )
			}""", 
			"Publication RDF data about E-GEOD-25759 not found!"
		)
	# /end: test_rdf_ae_experiments ()		
# /end: AeTest			

if __name__ == '__main__':
	unittest.main()
