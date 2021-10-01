import unittest
from biotools.bioportal import BioPortalClient, AgroPortalClient
from biotools import bioportal
import json

class BioPortalTest ( unittest.TestCase ):
	
	def __init__ ( self, method_name ):
		bioportal.is_debug = True # TODO: proper logging
		super().__init__ ( method_name )

		# this is what their UI, but probably they don't like that others reuse it
		self.bp = BioPortalClient ( "8b5b7825-538d-40e0-9e9e-5ab9274a9aeb" )
	
	def test_basics ( self ):
		#terms = bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin", cutoff = 3, ontologies = "MESH,SNOMED,ICD10" )
		terms = self.bp.annotator_terms ( "Melanoma is a malignant tumor usually affecting the skin", cutoff = 20 )
		#print ( "Text Annotator results:\n" + str ( terms ) )
		
		probe = [ term for term in terms if term [ "uri" ] == "http://purl.bioontology.org/ontology/CSP/2020-2434" ]
		self.assertTrue ( probe, "Test term not returned!" )
		self.assertTrue ( len ( probe ) == 1, "Too many test terms returned!" )
		probe = probe [ 0 ]
		self.assertEqual ( "melanoma", probe [ "label" ], "Test label not fetched!" )
		self.assertTrue ( "may occur in the skin of any part of the body" in probe [ "definition" ], "Wrong test definition!" )
		


class AgroPortalTest ( unittest.TestCase ):
	
	def __init__ ( self, method_name ):
		bioportal.is_debug = True # TODO: proper logging
		super().__init__ ( method_name )

		# this is what their UI, but probably they don't like that others reuse it
		self.ap = AgroPortalClient ( "1de0a270-29c5-4dda-b043-7c3580628cd5" )
	
	def test_basics ( self ):
		opts = {
			"ontologies": "CO_330,CO_321,TO,CO_121,AFO,EO,AEO,NCBITAXON,AGROVOC,FOODON", 
			"longest_only": "true",
			"exclude_numbers": "false",
			"whole_word_only": "true",
			"exclude_synonyms": "false",
		  "expand_mappings": "false",
		  "fast_context": "false",
		  "certainty": "false",
		  "temporality": "false",
		  "experiencer": "false",
		  "negation": "false",
		  "score": "cvalue"			
		}
		text = "CaPUB1, a Hot Pepper U-box E3 Ubiquitin Ligase, Confers Enhanced Cold Stress Tolerance and " 
		text += "Decreased Drought Stress Tolerance in Transgenic Rice (Oryza sativa L.)"
		terms = self.ap.annotator_terms ( text, cutoff = 5, **opts )
		# print ( terms )

		probe = [ term for term in terms if term [ "uri" ] == "http://purl.obolibrary.org/obo/NCBITaxon_4530" ]
		self.assertTrue ( probe, "Test term not returned!" )
		self.assertTrue ( len ( probe ) == 1, "Too many test terms returned!" )
		probe = probe [ 0 ]
		self.assertEqual ( "Oryza sativa", probe [ "label" ], "Test label not fetched!" )
		self.assertTrue ( "rice" in probe [ "synonyms" ], "Test synonym not fetched!" )


if __name__ == '__main__':
	unittest.main()
