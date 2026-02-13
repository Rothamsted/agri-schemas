from assertpy import assert_that
import pytest

from agrischemas.clients.ebigxa.gxa import (
	FetchGeneExpressionResult, fetch_gene_expression, fetch_gene_expression_counts, GeneExpressionCounts, 
	search_studies, search_study_accessions, SearchStudiesResult, AnalysisType, TechnologyType
)

from logging import getLogger

log = getLogger ( __name__ )

@pytest.mark.integration
def test_search_study_accessions ():
	tax_id = "3702"
	keywords = '"protein*" AND meristem'

	expected_accs = [ "E-GEOD-34476", "E-GEOD-75507", "E-GEOD-59167" ]
	result = list ( search_study_accessions ( keywords = keywords, tax_id = tax_id, result_limit = 10 ) )

	assert_that ( [ acc for acc, _ in result ], "Result contains the expected accessions" )\
		.contains ( *expected_accs )
	assert_that ( all ( score > 0 for _, score in result ), "Scores are valid" ).is_true ()

@pytest.mark.integration
def test_search_studies ():
	tax_id = "3702"
	# Lucene Syntax is translated into the format accpeted by bif:contains in Virtuoso.
	# HOWEVER, Lucene isn't fully supported, see the implementation of lucene_to_bif_contains() 
	# and its tests for details. 
	keywords = "protein* meristem" 

	expected_accs = [ "E-GEOD-34476", "E-GEOD-75507", "E-GEOD-59167" ]
	result: SearchStudiesResult = search_studies ( keywords = keywords, tax_id = tax_id, result_limit = 10 )

	assert_that ( result.studies.keys (), "Result contains the expected accessions" )\
		.contains ( *expected_accs )
	assert_that ( all ( score > 0 for score in result.study2text_score.values () ), "Scores are valid" ).is_true ()

	test_acc = "E-GEOD-34476"
	test_study = result.studies.get ( test_acc )
	assert_that ( test_study, "Test study contains expected properties" )\
		.has_accession ( test_acc )\
		.has_uri ( f"http://knetminer.org/data/rdf/resources/exp_{test_acc}" )\
		.has_analysis_type ( AnalysisType.DIFFERENTIAL )\
		.has_technology_type ( TechnologyType.RNA_SEQ )

	
	assert_that ( test_study.title, "Test study has the right title" )\
		.contains ( "Arabidopsis shoot meristem transcriptome during floral" )
	assert_that ( test_study.description, "Test study has the right description" )\
		.contains ( "mRNA levels in shoot apical meristems at 3 time points" )
	

@pytest.mark.integration
def test_fetch_gene_expression ():
	gene_accs = [ "AT1G01520", "AT1G01580", "AT1G01600" ]
	study_accs = [ "E-GEOD-75507" ]
	result: FetchGeneExpressionResult = fetch_gene_expression ( gene_accs = gene_accs, study_accs = study_accs )
	log.info ( f"Result:\n{result}" )
	assert_that ( result.gene2expression_levels.keys (), "Result contains expression levels" )\
		.contains_only ( *gene_accs )
	assert_that ( result.conditions, "Result has 2 conditions" ).is_length ( 2 )
	assert_that ( 
		[cond for cond in result.conditions.values () if cond.is_base_condition],
		"Result has 1 base condition" 
	).is_length ( 1 )
	
	test_gene_acc = "AT1G01520"
	assert_that ( 
		result.gene2expression_levels [ test_gene_acc ], "Test gene has 1 expression level" 
	).is_length ( 1 )

	level = result.gene2expression_levels [ test_gene_acc ] [ 0 ]
	assert_that ( level.study_acc, "Test level has the right study accession" )\
		.is_equal_to ( "E-GEOD-75507" )

	assert_that ( level.pvalue, "Test level has a valid p-value" )\
		.is_instance_of ( float )\
		.is_less_than ( 0.05 )
	
	assert_that ( abs ( level.log2fc ), "Test level has a valid log2 fold change" )\
		.is_instance_of ( float )\
		.is_greater_than ( 1 )
	
	assert_that ( level.condition_uri in result.conditions, "Test level has a valid condition URI" )\
		.is_true ()
	
	assert_that ( 
		result.conditions [ level.base_condition_uri ].is_base_condition, 
		"Test level has a valid base condition URI"
	).is_true ()


@pytest.mark.integration
def test_fetch_gene_expression_counts ():
	expected_result: GeneExpressionCounts = GeneExpressionCounts (
    gene_study_up_counts = {
			("AT1G07135", "E-MTAB-7612"): 5,
			("AT1G78460", "E-GEOD-37553"): 2,
			("AT1G06120", "E-MTAB-5132"): 1,
			("AT1G78460", "E-MTAB-7612"): 3
    },
    gene_study_down_counts = {
			("AT1G78460", "E-GEOD-57145"): 2,
			("AT1G06120", "E-MTAB-7612"): 5,
    },	
	)
	expected_result.gene_up_counts = { 
		gacc: sum (
				count
				for (g, _), count in expected_result.gene_study_up_counts.items()
				if g == gacc
		)
		for (gacc, _) in expected_result.gene_study_up_counts.keys()
	}
	expected_result.gene_down_counts = { 
    gacc: sum (
        count
        for (g, _), count in expected_result.gene_study_down_counts.items()
        if g == gacc
    )
    for (gacc, _) in expected_result.gene_study_down_counts.keys()
	}

	study_accs = [ acc for _, acc in expected_result.gene_study_up_counts.keys () ] \
		+ [ acc for _, acc in expected_result.gene_study_down_counts.keys () ]
	gene_accs = [ gacc for gacc, _ in expected_result.gene_study_up_counts.keys () ] \
		+ [ gacc for gacc, _ in expected_result.gene_study_down_counts.keys () ]
	
	# And here we go!
	result = fetch_gene_expression_counts ( gene_accs = gene_accs, study_accs = study_accs )
	assert_that ( result, "Result is correct" ).is_equal_to ( expected_result )
	