# gxa_rdf_all_save ( EXPERIMENTS_JS [ wildcards.exp_acc ], fout, compress = True )

import pytest
from rdflib import Graph
from agrischemas.ebigxa.gxa import gxa_get_analysis_types, gxa_rdf_all, gxa_rdf_all_save
from agrischemas.etltools.utils import sparql_ask

import logging

log = logging.getLogger ( __name__ )

@pytest.fixture ( scope = "module", name = "gxa_analysis_types" )
def fetch_gxa_analysis_types () -> dict [str, str]:
	gxa_analysis_types = gxa_get_analysis_types ( [ "arabidopsis thaliana" ] )
	return gxa_analysis_types

@pytest.mark.skip ( reason = "Not a real unit test, used to verify an experiment" )
def test_gxa_rdf_all_save_E_MTAB_3287 ( gxa_analysis_types ):
	"""
	Sometimes it isn't in the result of :func:`gxa_get_analysis_types`. This appears to be
	randomly, maybe due with some issue with the GXA or BioStudies API.
	"""
	acc = "E-MTAB-3287"
	gxa_rdf_all_save ( acc, gxa_analysis_types [ acc ], f"/tmp/{acc}.ttl" ) 

@pytest.mark.skip ( reason = "Too time consuming and already covered elsewhere" )
def test_dex_conditions_parsing_E_MTAB_8326 ():
	"""
	This isn't picking time point conditions from the level table.

	This experiment is tested in `gxa_test.py::GxaTest::test_rdf_gxa_dex_levels_microarray()`,
	but here we target it specifically, rather than having several other experiments in the way.
	"""
	acc = "E-MTAB-8326"

	# gxa_rdf_all_save ( acc, "Differential", f"/tmp/{acc}.ttl" ) 
	rdf_str = gxa_rdf_all ( acc, "Differential", out = None )

	graph = Graph ().parse ( data = rdf_str, format = "turtle" )

	assert sparql_ask ( 
		graph, 
		"""
		ASK {
			?levelStmt a rdf:Statement;
				rdf:subject ?gene;
				rdf:predicate bioschema:expressedIn;
				rdf:object bkr:cond_vip2_overexpression;
				agri:baseCondition bkr:cond_wild_type_genotype;
				agri:log2FoldChange ?foldChange;
				agri:pvalue ?pvalue;
				agri:evidence bkr:exp_E-MTAB-8326;
				agri:timePoint ?timePoint
			.
		}
		""" 
	), "0 hour time point level not found"

	assert sparql_ask ( 
		graph, 
		"""
		ASK {
			?levelStmt a rdf:Statement;
				rdf:subject ?gene;
				rdf:predicate bioschema:expressedIn;
				rdf:object bkr:cond_vip2_overexpression;
				agri:baseCondition bkr:cond_wild_type_genotype;
				agri:timePoint ?timePoint
			.

			?timePoint a agri:ExperimentalFactorValue;
				schema:name "0 hours";
				schema:value 0;
				schema:unitText "hour"
			.
		}
		""" 
	), "0 hour time point definition not found"
