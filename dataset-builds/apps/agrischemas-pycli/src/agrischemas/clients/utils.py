
import logging
from typing import Any, Generator
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

from agrischemas.clients.config import AGRISCHEMAS_SPARQL_ENDPOINT
import json as json_module

import requests

log = logging.getLogger( __name__ )

# TODO: Use XNamespaceManager.
AGRISCHEMAS_SPARQL_NAMESPACE_HEADER = \
	"""
	PREFIX bk: <http://knetminer.org/data/rdf/terms/biokno/>
	PREFIX bkr: <http://knetminer.org/data/rdf/resources/>
	PREFIX bkg: <http://knetminer.org/data/rdf/resources/graphs/>
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX owl: <http://www.w3.org/2002/07/owl#>
	PREFIX dc: <http://purl.org/dc/elements/1.1/>
	PREFIX dcterms: <http://purl.org/dc/terms/>
	PREFIX agri: <http://agrischemas.org/>
	PREFIX bioschema: <https://bioschemas.org/>
	PREFIX schema: <https://schema.org/>
	PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
	"""

ME_NS = "http://knetminer.org/data/rdf/terms/local/"

def sparql_run_construct ( 
	sparql_query: str,
	sparql_params: dict[str, Any] | None = None,
	sparql_endpoint: str | Graph = AGRISCHEMAS_SPARQL_ENDPOINT 
) -> dict[Any, Any]:
	"""
	Run a SPARQL CONSTRUCT query against the given endpoint, and return the result as a JSON dictionary.

	## Parameters
	- `sparql_query`: the SPARQL CONSTRUCT query to run, with placeholders for parameters in the form `?paramName`

	- `sparql_params`: a dictionary of parameters to substitute into the query, where the keys are the parameter 
		 names (without the `?`), and the values are the values to substitute.
		 **WARNING**: these values must be given in SPARQL syntax, **NOT** as `Literal` or `URIRef` objects.
		 That's because it's simpler, and also because we do the placeholder substitution ourselves, 
		 since rdflib's `initBindings` doesn't work with Virtuoso.

	## Returns
	A JSON dictionary that represents the result in JSON-LD format. This means you need to deal with
	stuff like `@id` and `@value` arrays, see the tests for examples.
	"""

	sparql_query = sparql_inject_params ( sparql_query, sparql_params )

	if isinstance ( sparql_endpoint, str ):
		# rdflib still works decently for CONSTRUCT, but not SELECT (see below)
		store = SPARQLStore ( sparql_endpoint )
		sparql_endpoint = Graph ( store )

	construct_graph = sparql_endpoint.query ( sparql_query ).graph
	json = construct_graph.serialize ( format = "json-ld" )

	# It's a JSON string, let's parse it into a dictionary
	json = json_module.loads ( json )

	return json

def sparql_run ( 
	sparql_query: str,
	sparql_params: dict[str, Any] | None = None,
	sparql_endpoint: str | Graph = AGRISCHEMAS_SPARQL_ENDPOINT 
) -> Generator[ dict[str, Any], None, None ]:
	"""
	Run a SPARQL SELECT query against the given endpoint, and return the result as a generator of dictionaries.
	"""

	sparql_query = sparql_inject_params ( sparql_query, sparql_params )
	if isinstance ( sparql_endpoint, str ):
		# Use HTTP-level querying, since rdflib is awful (see below)
		return _sparql_run_select_remote ( sparql_query, sparql_endpoint )

	# Else, it's a Graph
	result = sparql_endpoint.query ( sparql_query )

	return ( { str(var): row[ var ].toPython () for var in result.vars } for row in result )

def _sparql_run_select_remote (
    sparql_query: str,
    sparql_endpoint: str,
    accept: str = "application/sparql-results+json"
) -> Generator[dict[str, Any], None, None]:
	"""
	Run a SPARQL SELECT query against a remote endpoint, by using HTTP.

	We bypass rdflib for SELECT, because it sucks at handling Virtuoso's SPARQL endpoint, 
	eg, it tries to parse the returing SPARQL/XML as if it were RDF/XML.
	"""

	headers = {"Accept": accept}
	response = requests.post(
		sparql_endpoint,
		data={"query": sparql_query},
		headers=headers
	)
	response.raise_for_status()
	results = response.json()
	return (
		{var: binding[var]["value"] for var in results["head"]["vars"]}
		for binding in results["results"]["bindings"]
	)


def sparql_inject_params ( sparql_query: str, sparql_params: dict[str, Any] ) -> str:
	"""
	Inject parameters into a SPARQL query, replacing placeholders in the form `?paramName` with the corresponding values from `sparql_params`.

	**WARNING**: the values in `sparql_params` must be given in SPARQL syntax, **NOT** as `Literal` or `URIRef` objects.
	That's because it's simpler, and also because we do the placeholder substitution ourselves, since rdflib's `initBindings` doesn't work with Virtuoso.
	"""

	if not sparql_params: return sparql_query

	for param, value in sparql_params.items():
		placeholder = "?" + param
		if placeholder not in sparql_query:
			log.debug ( f"SPARQL query doesn't contain placeholder {placeholder}, skipping substitution" )
		sparql_query = sparql_query.replace ( placeholder, value )

	return sparql_query

def strings_2_sparql_list ( strings: Generator[str, None, None], do_wrapping: bool = False ) -> str:
	"""
	Convert the input into a SPARQL list, in the form `("string1" "string2" "string3")`.
	"""

	if strings is None: strings = []
	result = ", ".join ( f'"{s}"' for s in strings )
	if do_wrapping: result = f"( {result} )"
	return result