from agrischemas.clients.utils import sparql_run_construct
from rdflib import Graph

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

		ex:a ex:relatedTo ex:b.

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

		?person ex:relatedTo ?friend.
		
		?friend rdfs:label ?friendLabel.
	}
	"""

	sparql_params = { "person": "http://example.org/a" }
	result = sparql_run_construct ( sparql_query, sparql_params, sparql_endpoint = g )

	assert_that ( result, "Result type is correct" ).is_instance_of ( dict )
	assert_that ( result, "Result has the expected data" )\
		.contains_entry ( 
			"http://example.org/a",
			{ 
				"http://example.org/label": [ { "value": "Example A" } ],
				"http://example.org/friendLabel": [ { "value": "Example B" } ]
			}
		)	
