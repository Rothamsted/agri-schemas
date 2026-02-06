
import logging
from typing import Any
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

from agrischemas.clients.config import AGRISCHEMAS_SPARQL_ENDPOINT
import json as json_module

log = logging.getLogger( __name__ )


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

	if sparql_params:
		# As said above, `initBindings` in `Graph.query` messes up with Virtuoso, since rdflib translates
		# that into VALUES, but Virtuoso doesn't support this syntax when using CONSTRUCT, so let's go in
		# if-you-need-a-hand-you-find-it-at-the-end-of-your-arm mode.
		for param, value in sparql_params.items():
			placeholder = "?" + param
			if placeholder not in sparql_query:
				log.debug ( f"SPARQL query doesn't contain placeholder {placeholder}, skipping substitution" )
			sparql_query = sparql_query.replace ( placeholder, value )

		# with a SPARQL endpoint, so we have to do the substitution ourselves

	if isinstance ( sparql_endpoint, str ):
		store = SPARQLStore ( sparql_endpoint )
		sparql_endpoint = Graph ( store )

	construct_graph = sparql_endpoint.query ( sparql_query ).graph
	json = construct_graph.serialize ( format = "json-ld" )

	# It's a JSON string, let's parse it into a dictionary
	json = json_module.loads ( json )

	return json
