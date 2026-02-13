"""
TODO: comment me!
"""

from dataclasses import dataclass, field
import enum
from typing import Generator
from agrischemas.clients.config import AGRISCHEMAS_SPARQL_ENDPOINT
from agrischemas.clients.utils import (
	ME_NS, sparql_run_construct, sparql_run, AGRISCHEMAS_SPARQL_NAMESPACE_HEADER,
	strings_2_sparql_list
)

from agrischemas.etltools.virtuoso import lucene_to_bif_contains

from logging import getLogger
log = getLogger ( __name__ )

class TechnologyType ( enum.Enum ):
	RNA_SEQ = "RNA-seq of coding RNA"
	MICROARRAY = "Transcription Profiling by Array"


class AnalysisType ( enum.Enum ):
	"""
	The analysis types that we support in the AgriSchemas data sets

	These corresponds to [the RDF definitions](https://github.com/Rothamsted/agri-schemas/blob/master/dataset-builds/agrischemas-gxapy/src/agrischemas/ebigxa/gxa-rdf-defaults.ttl)
	"""
	DIFFERENTIAL = "EBI/GXA Differential Gene Expression Analysis"
	BASELINE = "EBI/GXA Baseline Gene Expression Analysis"


@dataclass
class Study:
	uri: str
	"""
	The AgrisSchemas data URI for the study
	"""
	accession: str
	"""
	The EBI/GXA study accession, e.g. E-MTAB-1234
	"""
	description: str

	tax_id: str
	"""
	The NCBI taxonomy ID for the species, e.g. 3702 for Arabidopsis thaliana
	"""
	
	title: str
	
	analysis_type: AnalysisType
	technology_type: TechnologyType

@dataclass
class GeneExpressionCondition:
	"""
	A condition under which a gene results expressed, according to GXA data about a study.
	"""

	uri: str
	"""
	The AgrisSchemas data URI for the condition. Note that conditions don't have accessions, 
	since they're synthetised from GXA labels.
	"""

	label: str

	onto_term_uris: list[str]
	"""
	The URIs of the ontology terms that were associated to the condition via AgroPortal or BioPortal 
	Annotator.
	"""

	numeric_value: float | None
	"""
	If the condition is about a numeric quantity, such as a time point, this is its value.

	At the moment we track time points only, and their identification is based on parsing text labels,
	so the results aren't always perfect.
	"""
	unitText: str | None

	is_base_condition: bool = False
	"""
	Differential analyses compare the gene expression of a gene in a condition relative (fold change) to 
	a base condition. The :class:`GeneExpressionLevel` class report both and this flag is set when a 
	condition is a base condition. This is useful in :class:`SearchStudiesResult`.
	"""

	is_time_point: bool = False
	"""
	Whether the condition is a time point, such as "3 days after germination". 
	In that case, the numeric value and unitText fields are non-null.
	"""

@dataclass
class OntoTerm:
	uri: str
	label: str | None
	accession: str | None


@dataclass
class SearchStudiesResult:
	"""
	The result of study search, see :func:`search_studies`.
	"""


	studies: dict[str, Study] = field ( default_factory = dict )
	"""
	A map of study accession -> Study
	"""

	study2conditions: dict[str, list[str]] = field ( default_factory = dict )

	"""
	For each study accession, the list of condition URIs such that there is some gene expressed under the conditions
	and the study is evidence of that.

	The AgriSchemas data have some minimum filtering over significance, so this might might not reflect 
	all the data in GXA.
	"""

	study2text_score: dict[str, float] = field ( default_factory = dict )
	"""
	For each study accession, the score of the text search, based on full text indexes. 

	This is a (weighted) combination of scores on study fields and condition labels (including ontology terms), so it reflects how well the study matches the search keywords, but it's not a measure of how relevant the study is for the conditions of interest.
	"""

	conditions: dict[str, GeneExpressionCondition] = field ( default_factory = dict )
	"""
	A map of condition URI -> details.
	"""

	onto_terms: dict[str, OntoTerm] = field ( default_factory = dict )
	"""
	A map of ontology term URI -> details.
	"""


@dataclass
class GeneExpressionLevel:
	"""
	Represents a result item from gene expression level search, see 
	:func:`fetch_gene_expression` and :func:`fetch_gene_expression_by_condition`.
	"""

	uri: str
	"""
	Uniquely identifies the combination of gene, study and conditions that an expression level 
	groups together.
	"""

	gene_acc: str
	
	study_acc: str
	"""
	The evidence for this expression level, that is, the study providing the data and the analysis 
	on which this level is based.

	Here, we don't return study details, since there are other functions for that.
	"""

	condition_uri: str
	"""
	The condition under which the gene is expressed at this level.
	"""

	base_condition_uri: str
	"""
	The base condition to which the condition_uri is compared to compute the log2 fold change.

	See the description of :attr:`GeneExpressionCondition.is_base_condition` for details.
	"""

	log2fc: float = 0
	"""
	The log2 [fold change](https://en.wikipedia.org/wiki/Fold_change) of the gene expression level in the condition compared to the base condition.

	This represents the intensity of the relative gene expression in the condition vs base condition.
	0 means no change (usually not in AgriSchemas data, due to the filtering we do).
	Positive values mean up-regulation, negative values mean down-regulation.
	"""

	pvalue: float = 1
	"""
	The [p-value](https://en.wikipedia.org/wiki/P-value) of the gene expression level.

	This represents the statistical significance of the gene expression level, that is, how likely it, 
	according to the data, that the observed differential expression at issue (ie, the fold change) is due 
	to random chance. Hence, 0 = it's relevant, cause didn't happen by chance, 1 = ignore it, since it is completely
	likely to be due to random chance.

	The p-value in a differential gene expression analysis is computed by methods like ANOVA, 
	see the GXA documentation for details, we just trust and import their data (after filtering from some
	max cutoff).
	
	"""


@dataclass
class FetchGeneExpressionResult:
	"""
	The result of gene expression level search, see :func:`fetch_gene_expression` and :func:`fetch_gene_expression_by_condition`.
	"""
	
	gene2expression_levels: dict[str, list[GeneExpressionLevel]] = field ( default_factory = dict )
	"""
	A map of gene accession -> list of expression levels for that gene.
	"""

	conditions: dict[str, GeneExpressionCondition] = field ( default_factory = dict )
	"""
	A map of condition URI -> details.
	"""

	onto_terms: dict[str, OntoTerm] = field ( default_factory = dict )
	"""
	A map of ontology term URI -> details.
	"""


@dataclass
class GeneExpressionCounts:
	"""
	Represents per-gene counts of conditions in which the genes result expressed according to GXA data.
	This is what functions like :func:`fetch_gene_expression_counts` return.
	"""

	gene_up_counts: dict[str, int] = field ( default_factory = dict )
	"""
	gene accession -> number of conditions in which the gene is up-regulated.
	"""

	gene_down_counts: dict[str, int] = field ( default_factory = dict )
	"""
	gene accession -> number of conditions in which the gene is down-regulated.
	"""

	gene_study_up_counts: dict[tuple[str, str], int] = field ( default_factory = dict )
	"""
	gene accession, study accession -> number of conditions in which the gene is up-regulated.
	The gene x study counts are not very significant, since mostly they're around 1.
	"""

	gene_study_down_counts: dict[tuple[str, str], int] = field ( default_factory = dict )
	"""
	gene accession, study accession -> number of conditions in which the gene is down-regulated.
	The gene x study counts are not very significant, since mostly they're around 1.
	"""


def search_study_accessions ( keywords: str, tax_id: str, result_limit: int = 1000 ) -> Generator[tuple[str, float]]:
	"""
	TODO: comment me!
	
	TODO: use Elastic and move away from the rubbish bif:contains()
	TODO: add publication fields
	"""

	query = AGRISCHEMAS_SPARQL_NAMESPACE_HEADER + \
	"""

	SELECT ?acc ?score
	WHERE
	{
		?study a bioschema:Study ;
				schema:identifier ?acc;
				dc:title ?title ;
				schema:description ?desc .

		?specie schema:subjectOf ?study;
			bioschema:taxonomicRange ?taxon
		.

		BIND ( REPLACE ( STR ( ?taxon ), "http://purl.bioontology.org/ontology/NCBITAXON/", "" ) AS ?taxId )
  	FILTER ( ?taxId = "?paramTaxId" )

		# TODO: for now, we are interested in differential analyses only, remove if 
		# you want to extend it to baseline.
		#
		?study bioschema:studyProcess/schema:additionalProperty bkr:gxa_analysis_type_differential.

		OPTIONAL { ?study dc:title ?title. ?title bif:contains "?paramKeywords" OPTION ( SCORE ?titleScore ) } 
		OPTIONAL { ?study schema:description ?description. ?description bif:contains "?paramKeywords" OPTION ( SCORE ?descriptionScore ) } 
		OPTIONAL { ?study schema:identifier ?acc. ?acc bif:contains "?paramKeywords" OPTION ( SCORE ?accScore ) } 

		FILTER ( BOUND ( ?titleScore ) OR BOUND ( ?descriptionScore ) OR BOUND ( ?accScore ) )

		BIND ( COALESCE ( ?titleScore, 0 ) AS ?titleScoreNorm )
		BIND ( COALESCE ( ?descriptionScore, 0 ) AS ?descriptionScoreNorm )
		BIND ( COALESCE ( ?accScore, 0 ) AS ?accScoreNorm )

		BIND ( 3 * ?accScoreNorm + 2 * ?titleScoreNorm + ?descriptionScoreNorm  AS ?score )
	}
	ORDER BY DESC ( ?score )
	LIMIT ?paramResultLimit
  """

	return ( (row [ 'acc' ], float ( row [ 'score' ] ) )
		for row in
			sparql_run ( 
				query, 
				sparql_params = { 
					"paramKeywords": lucene_to_bif_contains ( keywords ),
					"paramTaxId": tax_id,
					"paramResultLimit": str ( result_limit ) 
				}
			) 
	)




def search_studies ( keywords: str, tax_id: str, result_limit: int = 1000 ) -> SearchStudiesResult:
	"""
	Searches studies by keywords. The keywords are searched in relevant study and condition fields
	(title, description, etc).

	A condition is considered linked to the study when there is at least one gene expressed under the condition
	and based on the study data as evidence. (TODO: still missing)

	The search score is computed by weighting scores in the various searched fields.
	"""

	# First, the accessions
	accs_n_scores = search_study_accessions ( keywords, tax_id, result_limit )
	if not accs_n_scores: return SearchStudiesResult ()

	accs_n_scores = { acc: score for acc, score in accs_n_scores }
	accs = accs_n_scores.keys ()

	# Then the details, by filtering with accessions
	query = AGRISCHEMAS_SPARQL_NAMESPACE_HEADER + \
	"""

	SELECT ?study ?acc ?title ?description ?gxaAnalysis ?aeTech
	WHERE {
		?study schema:identifier ?acc.

		FILTER ( ?acc IN ( ?paramAccs ) ).

		?study
			dc:title ?title ;
			schema:description ?description;
			bioschema:studyProcess ?design.

		?design schema:additionalProperty ?gxaAnalysis, ?aeTech.

		?gxaAnalysis schema:propertyID "gxaAnalysisType".
		?aeTech schema:propertyID "aeTechnologyType".
	}
	"""
	BKR_NS = "http://knetminer.org/data/rdf/resources/"

	def gxa_analysis_uri_2_enum ( uri: str ) -> AnalysisType:
		if uri == f"{BKR_NS}gxa_analysis_type_differential":
			return AnalysisType.DIFFERENTIAL
		elif uri == f"{BKR_NS}gxa_analysis_type_baseline":
			return AnalysisType.BASELINE
		else:
			raise ValueError ( f"Unknown GXA analysis type URI: {uri}" )
	def ae_tech_uri_2_enum ( uri: str ) -> TechnologyType:
		if uri == f"{BKR_NS}ae_technology_type_microarray":
			return TechnologyType.MICROARRAY
		elif uri == f"{BKR_NS}ae_technology_type_rna_sequencing":
			return TechnologyType.RNA_SEQ
		else:
			raise ValueError ( f"Unknown AE technology type URI: {uri}" )
		
	result = SearchStudiesResult ()
	result.study2text_score = accs_n_scores

	sparql_params = { "paramAccs": strings_2_sparql_list ( accs ) }
	for row in sparql_run ( query, sparql_params = sparql_params ):
		study_uri, study_acc, title, description, analysis_type, technology_type = \
			row [ 'study' ], row [ 'acc' ], row [ 'title' ], row [ 'description' ], \
			gxa_analysis_uri_2_enum ( row [ 'gxaAnalysis' ] ), \
			ae_tech_uri_2_enum ( row [ 'aeTech' ] )

		result.studies [ study_acc ] = Study (
			uri = study_uri,
			accession = study_acc,
			title = title,
			description = description,
			analysis_type = analysis_type,
			technology_type = technology_type,
			tax_id = tax_id
		)

	return result


def fetch_gene_expression ( 
	gene_accs: list[str], study_accs: list[str], pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0 
) -> FetchGeneExpressionResult:
	"""
	Gets gene expression levels for the given genes and studies, filtered by p-value and log2 fold change cutoffs.

	Usually, you get the study accessions from :func:`search_studies`.

	TODO: optional study_accs?
	"""

	query = AGRISCHEMAS_SPARQL_NAMESPACE_HEADER + \
	f"\nPREFIX : <{ME_NS}>\n" + \
	"""
	CONSTRUCT 
	{
		?expStatement a :ExpStatement;
			:geneAcc ?geneAcc;
			:studyAcc ?studyAcc;
			:condition ?condition;
			:baseCondition ?baseCondition;
			:log2fc ?log2fc;
			:pvalue ?pvalue
		.

		?condition a :Condition;
			:label ?condLabel;
			:value ?numericValue;
			:unitText ?unitText;
			:ontoTerm ?condOntoTerm
		.

		?condOntoTerm a :OntoTerm;
			:ontoTermAcc ?ontoTermAcc;
			:ontoTermLabel ?ontoTermLabel
		.

		?baseCondition a :BaseCondition;
			:label ?baseCondLabel;
			:value ?baseNumericValue;
			:unitText ?baseUnitText;
			:ontoTerm ?baseCondOntoTerm
		.

		?baseCondOntoTerm a :OntoTerm;
			:ontoTermAcc ?baseOntoTermAcc;
			:ontoTermLabel ?baseOntoTermLabel
		.
	}
	WHERE {
		?gene a bioschema:Gene;
				schema:identifier ?geneAcc.

		# Let''s focus on a few genes
		FILTER ( UCASE (STR ( ?geneAcc ) ) IN ( ?paramGeneAccs ) )  


		?gene bioschema:expressedIn ?condition.

		?expStatement a rdf:Statement;
			rdf:subject ?gene;
			rdf:predicate bioschema:expressedIn;
			rdf:object ?condition;
			agri:baseCondition ?baseCondition;
			agri:evidence ?study
		.

		?study schema:identifier ?studyAcc.

		FILTER ( ?studyAcc IN ( ?paramStudyAccs ) )

		# Getting the significance scores
		{
			# Differential expression analysis
			?expStatement agri:pvalue ?pvalue; agri:log2FoldChange ?log2fc. 
			FILTER ( ?pvalue < ?paramPvalueCutoff && ABS ( ?log2fc ) > ?paramLog2fcCutoff )
		}
		# TODO: possibly, add baseline

		# Condition details
		?condition schema:name ?condLabel.

		# Numeric value (ie, time point)
		OPTIONAL {
		  ?condition schema:value ?numericValue; schema:unitText ?unitText.
		}

		# Ontology terms associated to the condition
		OPTIONAL {
			?condition dc:type ?condOntoTerm.
			OPTIONAL { ?condOntoTerm schema:identifier ?ontoTermAcc. }
			OPTIONAL { ?condOntoTerm schema:name ?ontoTermLabel }
		}

		# Base condition details
		?baseCondition schema:name ?baseCondLabel.

		# Numeric value (ie, time point)
		OPTIONAL {
			?baseCondition schema:value ?baseNumericValue; schema:unitText ?baseUnitText.
		}

		# Ontology terms associated to the base condition
		OPTIONAL {
			?baseCondition dc:type ?baseCondOntoTerm.
			OPTIONAL { ?baseCondOntoTerm schema:identifier ?baseOntoTermAcc. }
			OPTIONAL { ?baseCondOntoTerm schema:name ?baseOntoTermLabel }
		}	
	}
  """

	params = {
		"paramGeneAccs": strings_2_sparql_list ( gene_accs ),
		"paramStudyAccs": strings_2_sparql_list ( study_accs ),
		"paramPvalueCutoff": str ( pvalue_cutoff ),
		"paramLog2fcCutoff": str ( log2fc_cutoff )
	}

	result = FetchGeneExpressionResult ()
	construct_result = sparql_run_construct ( query, sparql_params = params )

	for item in construct_result:
		if item.get ( "@type", [ 'None' ] ) [ 0 ] == f"{ME_NS}ExpStatement":
			# TODO: this is bad, move these JSON-LD common patterns to utils.
			gene_acc = item [ f"{ME_NS}geneAcc" ] [ 0 ] [ "@value" ]
			study_acc = item [ f"{ME_NS}studyAcc" ] [ 0 ] [ "@value" ]
			condition_uri = item [ f"{ME_NS}condition" ] [ 0 ] [ "@id" ]
			base_condition_uri = item [ f"{ME_NS}baseCondition" ] [ 0 ] [ "@id" ]
			log2fc = float ( item [ f"{ME_NS}log2fc" ] [ 0 ] [ "@value" ] )
			pvalue = float ( item [ f"{ME_NS}pvalue" ] [ 0 ] [ "@value" ] )

			result.gene2expression_levels.setdefault ( gene_acc, [] ).append (
				GeneExpressionLevel (
					uri = item [ "@id" ],
					gene_acc = gene_acc,
					study_acc = study_acc,
					condition_uri = condition_uri,
					base_condition_uri = base_condition_uri,
					log2fc = log2fc,
					pvalue = pvalue
				)
			)
		elif item.get ( "@type", [ 'None' ] ) [ 0 ] in ( f"{ME_NS}Condition", f"{ME_NS}BaseCondition" ):
			cond_type = item.get ( "@type", [ 'None' ] ) [ 0 ]
			num_value = item.get ( f"{ME_NS}numericValue", [ { "@value": None } ] )[ 0 ] [ "@value" ]
			if num_value is not None: num_value = float ( num_value )
			cond = GeneExpressionCondition (
				uri = item [ "@id" ],
				label = item [ f"{ME_NS}label" ] [ 0 ] [ "@value" ],
				numeric_value = num_value,
				unitText = item.get ( f"{ME_NS}unitText", [ { "@value": None } ] )[ 0 ] [ "@value" ],
				onto_term_uris = [ onto_term_uri for onto_term_uri in item.get ( f"{ME_NS}ontoTerm", [] ) ],
				is_base_condition = cond_type == f"{ME_NS}BaseCondition",
				# TODO: for now, all numeric conds are time points.
				is_time_point = num_value is not None 
			)
			result.conditions [ cond.uri ] = cond
		elif item.get ( "@type", [ 'None' ] ) [ 0 ] == f"{ME_NS}OntoTerm":
			onto_term = OntoTerm (
				uri = item [ "@id" ],
				accession = item.get ( f"{ME_NS}ontoTermAcc", [ { "@value": None } ] )[ 0 ] [ "@value" ],
				label = item.get ( f"{ME_NS}ontoTermLabel", [ { "@value": None } ] )[ 0 ] [ "@value" ]
			)
			result.onto_terms [ onto_term.uri ] = onto_term
	# /for item in construct_result
	return result


def fetch_gene_expression_counts (
	gene_accs: list[str], study_accs: list[str] = [], pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0
) -> GeneExpressionCounts:
	"""
	Returns per-gene x study counts of the number of conditions in which they're
	up/down/total regulated, plus per-gene overall counts.

	`study_accs` is optional, if not provided, it counts against the provided genes over all studies.
	"""

	query = AGRISCHEMAS_SPARQL_NAMESPACE_HEADER + \
		"""
		SELECT ?geneAcc ?studyAcc ?regDirection (COUNT (?condition) AS ?conditions)
			WHERE {
				?gene a bioschema:Gene;
						schema:identifier ?geneAcc.

				# Let''s focus on a few genes
				FILTER ( UCASE (STR ( ?geneAcc ) ) IN ( ?paramGeneAccs ) )  


				?gene bioschema:expressedIn ?condition.

				?expStatement a rdf:Statement;
					rdf:subject ?gene;
					rdf:predicate bioschema:expressedIn;
					rdf:object ?condition;
					agri:evidence ?study
				.

				?study schema:identifier ?studyAcc.

				?paramStudyAccFilter

				# Getting the significance scores
							# Differential expression analysis

				?expStatement agri:pvalue ?pvalue; agri:log2FoldChange ?log2fc.
				FILTER ( ?pvalue < ?paramPvalueCutoff && ABS ( ?log2fc ) > ?paramLog2fcCutoff )

		BIND ( IF ( ?log2fc < 0, "DOWN", "UP" ) AS ?regDirection )

		}
		GROUP BY ?geneAcc ?studyAcc ?regDirection
		"""
	
	result: GeneExpressionCounts = GeneExpressionCounts ()

	params = {
		"paramGeneAccs": strings_2_sparql_list ( gene_accs ),
		"paramPvalueCutoff": str ( pvalue_cutoff ),
		"paramLog2fcCutoff": str ( log2fc_cutoff ),
		"paramStudyAccFilter": 
			( "FILTER (?studyAcc IN ( %s ))" % strings_2_sparql_list ( study_accs ) ) if study_accs else ""
	}
	for row in sparql_run ( query, sparql_params = params ):
		gene_acc, study_acc, reg_direction, conditions_count = \
			row [ 'geneAcc' ], row [ 'studyAcc' ], row [ 'regDirection' ], int ( row [ 'conditions' ] )
		if reg_direction == "UP":
			result.gene_up_counts [ gene_acc ] = result.gene_up_counts.get ( gene_acc, 0 ) + conditions_count
			result.gene_study_up_counts [ ( gene_acc, study_acc ) ] = conditions_count
		else:
			result.gene_down_counts [ gene_acc ] = result.gene_down_counts.get ( gene_acc, 0 ) + conditions_count
			result.gene_study_down_counts [ ( gene_acc, study_acc ) ] = conditions_count
	
	return result
		



	
	

def fetch_gene_expression_by_condition ( 
	gene_accs: list[str], cond_uris: list[str], 
	pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0 
) -> FetchGeneExpressionResult:
	"""
	TODO: I'm not sure we need this. Surely, we'll develop it later.
	"""
	pass


def fetch_gene_expression_counts_by_condition (
	gene_accs: list[str], cond_uris: list[str], 
	pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0
) -> GeneExpressionCounts:
	"""
	TODO: as for :func:`fetch_gene_expression_by_condition`, not sure we need this.
	"""
	pass