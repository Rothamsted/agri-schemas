import pytest
from agrischemas.clients.utils import sparql_run_construct
from rdflib import Graph, Literal, URIRef

from assertpy import assert_that

def test_sparql_run_construct_basic ():
	"""
	Tests that the `sparql_run_construct` against a local Graph
	"""
	g = Graph ()
	g.parse ( 
		# TODO: factorise namespaces
		data = """
		@prefix ex: <http://example.org/>.
		@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.

		ex:a a ex:Person;
			rdfs:label "Example A"
		.

		ex:a ex:knows ex:b.

		ex:b a ex:Person;
			rdfs:label "Example B"
		.
		""",
		format = "turtle" 
	)

	sparql_query = """
	PREFIX ex: <http://example.org/>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	CONSTRUCT {
		?person ex:label ?label;
			ex:friendLabel ?friendLabel.
	}
	WHERE {
		?person a ex:Person;
			rdfs:label ?label.

		?person ex:knows ?friend.
		?friend rdfs:label ?friendLabel.
	}
	"""

	sparql_params = { "person": "<http://example.org/a>" }
	result = sparql_run_construct ( sparql_query, sparql_params, sparql_endpoint = g )

	assert_that ( result, "Result type is correct" ).is_instance_of ( list )
	assert_that ( result, "Result isn't empty" ).is_not_empty ()
	result = result[ 0 ]
	assert_that ( result, "Result has the expected object" ).is_instance_of ( dict )
	assert_that ( result, "Result has the expected data" )\
		.is_equal_to ( 
			{ 
				"@id": "http://example.org/a",
				"http://example.org/label": [ { "@value": "Example A" } ],
				"http://example.org/friendLabel": [ { "@value": "Example B" } ]
			}
		)	


@pytest.mark.integration
def test_sparql_run_construct_knetminer_endpoint ():
	# TODO: as above, factorise namespaces
	sparql_query = """
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		PREFIX dc: <http://purl.org/dc/elements/1.1/>
		PREFIX dcterms: <http://purl.org/dc/terms/>
		PREFIX agri: <http://agrischemas.org/>
		PREFIX bioschema: <https://bioschemas.org/>
		PREFIX schema: <https://schema.org/>
		PREFIX : <https://foo.com/>

		CONSTRUCT {
			?study :title ?studyTitle;
				:accession ?studyAcc;
				:specie ?specieName.
		}
		WHERE {
			?study a bioschema:Study;
				dc:title ?studyTitle;
				schema:identifier ?studyAcc
			.

			?specie schema:subjectOf ?study;
				schema:name ?specieName.
		}"""
	
	sparql_params = { "studyAcc": '"E-GEOD-20227"' }
	result = sparql_run_construct ( sparql_query, sparql_params = sparql_params )

	assert_that ( result, "Result type is correct" ).is_instance_of ( list )
	assert_that ( result, "Result isn't empty" ).is_not_empty ()
	result = result[ 0 ]
	assert_that ( result, "Result has the expected object" ).is_instance_of ( dict )
	assert_that ( result, "Result has the expected data" )\
		.contains_entry ( 
			{ "https://foo.com/title": [ { "@value": "Novel Target Genes Regulated By LEUNIG" } ] },
			{ "https://foo.com/accession": [ { "@value": "E-GEOD-20227" } ] },
			{ "https://foo.com/specie": [ { "@value": "Arabidopsis thaliana" } ] }
		)
