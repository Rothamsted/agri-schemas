import unittest
from etltools.utils import logger_config, sparql_ask
from ebigxa.ae import ae_get_experiment_descriptors, rdf_ae_experiment
from ebigxa.utils import rdf_gxa_namespaces
import rdflib

log = logger_config ( __name__ )

class AeTest ( unittest.TestCase ):
	
	ae_exps = None
	
	@classmethod
	def setUpClass(cls):
		AeTest.ae_exps = ae_get_experiment_descriptors ( [ "arabidopsis thaliana", "triticum aestivum" ] ) 
		#log.info ( "EXPS:\n%s", ae_exps ) 
		
	def test_ae_descriptors ( self ):
		ara_acc = "E-MTAB-8326"
		self.assertTrue ( ara_acc in AeTest.ae_exps, "Arabidopsis experiment not found!" )
		# This is normally added by gxa.gxa_get_experiment_descriptors()
		AeTest.ae_exps [ ara_acc ] [ "gxaAnalysisType" ] = 'differential'
		
		wheat_acc = "E-GEOD-25759"
		self.assertTrue ( wheat_acc in AeTest.ae_exps, "Wheat experiment not found!" )
		AeTest.ae_exps [ wheat_acc ] [ "gxaAnalysisType" ] = 'differential'
		
		exp = AeTest.ae_exps [ ara_acc ]
		log.info ( exp )
		self.assertTrue ( 
			"Transcriptome analysis of Arabidopsis VIRE2-INTERACTING PROTEIN2" in exp [ "name" ],
			"Bad ara. experiment name!"
		)
		self.assertTrue ( 
			"C-terminal NOT2 domain of VIP2 interacts" in exp [ "description" ] [ 0 ] [ "text" ],
			"Bad ara. experiment description!"
		)
		self.assertEqual ( "2019-09-26", exp [ "lastupdatedate" ], "Bad experiment date" )
		self.assertEqual ( "Microarray", exp [ "aeTechnologyType" ], "Bad technology type" )
		
		
		exp = AeTest.ae_exps [ wheat_acc ]
		self.assertTrue ( 
			"Cantu D, Pearce SP, Distelfeld A" in exp [ "bibliography" ] [ 0 ] [ "authors" ],
			"Bad publication for wheat experiment!"
		)
		
	def test_rdf_ae_experiments ( self ):
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
					schema:additionalProperty bkr:gxa_analysis_type_differential.	
				
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


	def assert_rdf ( self, graph, ask_query, fail_msg ):
		self.assertTrue ( sparql_ask ( graph, ask_query ), fail_msg )		
			
		
if __name__ == '__main__':
	unittest.main()
