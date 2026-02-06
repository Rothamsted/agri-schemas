"""
TODO: comment me!
"""

import enum
from attr import dataclass

from agrischemas.clients.config import AGRISCHEMAS_SPARQL_ENDPOINT


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
	
	analysys_type: AnalysisType
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


	studies: dict[str, Study]
	"""
	A map of study accession -> Study
	"""

	study2conditions: dict[str, list[str]]
	"""
	For each study accession, the list of condition URIs such that there is some gene expressed under the conditions
	and the study is evidence of that.

	The AgriSchemas data have some minimum filtering over significance, so this might might not reflect 
	all the data in GXA.
	"""

	study2text_score: dict[str, float]
	"""
	For each study accession, the score of the text search, based on full text indexes. 

	This is a (weighted) combination of scores on study fields and condition labels (including ontology terms), so it reflects how well the study matches the search keywords, but it's not a measure of how relevant the study is for the conditions of interest.
	"""

	conditions: dict[str, GeneExpressionCondition]
	"""
	A map of condition URI -> details.
	"""

	onto_terms: dict[str, OntoTerm]
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
class GeneExpressionCounts:
	"""
	TODO: comment me!
	"""
	gene_study_up_counts: dict[tuple[str, str], int]
	gene_study_down_counts: dict[tuple[str, str], int]
	gene_up_counts: dict[str, int]
	gene_down_counts: dict[str, int]


def search_studies ( keywords: str, tax_id: str ) -> SearchStudiesResult:
	"""
	Searches studies by keywords. The keywords are searched in relevant study and condition fields
	(title, description, etc).

	A condition is considered linked to the study when there is at least one gene expressed under the condition
	and based on the study data as evidence. 
	"""
	pass

def fetch_gene_expression ( 
	gene_accs: list[str], study_accs: list[str], pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0 
) -> list[GeneExpressionLevel]:
	"""
	Gets gene expression levels for the given genes and studies, filtered by p-value and log2 fold change cutoffs.

	Usually, you get the study accessions from :func:`search_studies`.
	"""
	pass


def fetch_gene_expression_counts (
	gene_accs: list[str], study_accs: list[str], pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0
) -> GeneExpressionCounts:
	"""
	Returns a per-gene, per-study count of the number of conditions in which they're
	up/down/total regulated, plus per-gene overall counts.
	"""
	pass
	

def fetch_gene_expression_by_condition ( 
	gene_accs: list[str], cond_uris: list[str], 
	pvalue_cutoff: float = 0.05, log2fc_cutoff: float = 1.0 
) -> list[GeneExpressionLevel]:
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