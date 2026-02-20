
from agrischemas.etltools.utils import XNamespaceManager

AGRISCHEMAS_NS_MGR = XNamespaceManager()
AGRISCHEMAS_NS_MGR.load (
	data = """
	@prefix bk: <http://knetminer.org/data/rdf/terms/biokno/>.
	@prefix bkr: <http://knetminer.org/data/rdf/resources/>.
	@prefix bkg: <http://knetminer.org/data/rdf/resources/graphs/>.
	@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
	@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
	@prefix owl: <http://www.w3.org/2002/07/owl#>.
	@prefix dc: <http://purl.org/dc/elements/1.1/>.
	@prefix dcterms: <http://purl.org/dc/terms/>.
	@prefix agri: <http://agrischemas.org/>.
	@prefix bioschema: <https://bioschemas.org/>.
	@prefix schema: <https://schema.org/>.
	@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
	@prefix : <http://knetminer.org/data/rdf/terms/local/>.
	"""
)
"""
Common namespace definitions used in the AgriSchemas clients.
"""

ME_NS = AGRISCHEMAS_NS_MGR.ns ( ":" )
"""
A fictitious namespace, used for local purposes, such as building a graph with the SPARQL CONSTRUCT
clause.
"""

AGRISCHEMAS_SPARQL_ENDPOINT = "https://sparql-dev.knetminer.com/sparql"
"""
The SPARQL endpoint offering the AgriSchemas demo/reference datasets.
"""

# For hacky local tests
# AGRISCHEMAS_SPARQL_ENDPOINT = "http://localhost:8890/sparql"

