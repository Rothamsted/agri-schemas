from textwrap import dedent

"""
 The GXA-relevant namespaces
"""
def rdf_gxa_namespaces () -> str:
	rdf = """
		@prefix bkr: <http://knetminer.org/data/rdf/resources/> .
		@prefix agri: <http://agrischemas.org/> .
		@prefix bioschema: <http://bioschemas.org/> .
		@prefix schema: <https://schema.org/> .
		@prefix obo: <http://purl.obolibrary.org/obo/> .
		@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
		@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
		@prefix dc: <http://purl.org/dc/elements/1.1/> .
		@prefix ppeo: <http://purl.org/ppeo/PPEO.owl#>.
	"""
	return dedent ( rdf )
