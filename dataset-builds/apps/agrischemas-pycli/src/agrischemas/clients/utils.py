
from typing import Any
from rdflib import Graph
from agrischemas.clients.config import AGRISCHEMAS_SPARQL_ENDPOINT


def sparql_run_construct ( 
	sparql_query: str,
	sparql_params: dict[str, Any] | None = None,
	sparql_endpoint: str | Graph = AGRISCHEMAS_SPARQL_ENDPOINT 
) -> dict[Any, Any]:
	"""
	Run a SPARQL CONSTRUCT query against the given endpoint, and return the result as a JSON dictionary.
	"""
	if sparql_params is None: sparql_params = {}
