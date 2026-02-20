from typing import Generator
import pytest
from rdflib import Graph
from assertpy import assert_that

from agrischemas.etltools.sparql import sparql_run_construct, sparql_run
from agrischemas.config import AGRISCHEMAS_NS_MGR, ME_NS

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

	EX_NS = "http://example.org/"
	sparql_query = """
	PREFIX ex: <%s>
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
	""" % EX_NS

	sparql_params = { "person": f"<{EX_NS}a>" }
	result = sparql_run_construct ( sparql_query, sparql_params, sparql_endpoint = g )

	assert_that ( result, "Result type is correct" ).is_instance_of ( list )
	assert_that ( result, "Result isn't empty" ).is_not_empty ()
	result = result[ 0 ]
	assert_that ( result, "Result has the expected object" ).is_instance_of ( dict )
	assert_that ( result, "Result has the expected data" )\
		.is_equal_to ( 
			{ 
				"@id": f"{EX_NS}a",
				f"{EX_NS}label": [ { "@value": "Example A" } ],
				f"{EX_NS}friendLabel": [ { "@value": "Example B" } ]
			}
		)	


@pytest.mark.integration
def test_sparql_run_construct_knetminer_endpoint ():
	# TODO: as above, factorise namespaces
	sparql_query = AGRISCHEMAS_NS_MGR.to_sparql () + """

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
			{ f"{ME_NS}title": [ { "@value": "Novel Target Genes Regulated By LEUNIG" } ] },
			{ f"{ME_NS}accession": [ { "@value": "E-GEOD-20227" } ] },
			{ f"{ME_NS}specie": [ { "@value": "Arabidopsis thaliana" } ] }
		)
	
@pytest.mark.integration
def test_sparql_run_knetminer_endpoint ():
	sparql_query = AGRISCHEMAS_NS_MGR.to_sparql () + """
		SELECT ?studyAcc ?foo
		WHERE {
			?study a bioschema:Study;
				schema:identifier ?studyAcc
			.

			BIND ( CONCAT ( "'?fooParam' attached to ", STR ( ?studyAcc ) ) AS ?foo )
		}
		ORDER BY ?studyAcc
		LIMIT 3
		"""
	
	sparql_params = { "fooParam": 'foo value' }
	result = sparql_run ( sparql_query, sparql_params = sparql_params )

	assert_that ( result, "Result type is correct" ).is_instance_of ( Generator )
	result = list ( result )
	assert_that ( result, "Result has the expected length" ).is_length ( 3 )
	for test_acc in [ "E-ATMX-20", "E-ATMX-25", "E-ATMX-26" ]:
		assert_that ( result, "Result has the expected data" )\
		.contains ( { "studyAcc": test_acc, "foo": f"'foo value' attached to {test_acc}" } )
