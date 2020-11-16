from textwrap import dedent

from utils import make_id, print_rdf_namespaces
from gxa_common import process_gxa_experiments, make_condition_uri

# Gets GXA expression data and render them as RDF
#

print_rdf_namespaces ()

def print_exp_rdf ( exp_acc, gene_id, condition, tpm  ):
	rdf_tpl = """
		{gene} a bioschema:Gene;
			schema:identifier "{geneAcc}";
		.

		bkr:gxaexp_{experimentId}_{geneId}_{conditionId} a rdfs:Statement;
			agri:score "{level}";
			rdf:subject {gene};
			rdf:predicate bioschema:expressedIn;
			rdf:object {condition};
			agri:evidence {experiment}
		.
		
		{condition} a agri:StudyFactor;
			schema:name "{conditionLabel}"
		.

		{gene} bioschema:expressedIn {condition}.
	"""

	# TODO: it would be more correct to not change the case, but we want Knet compatibility in this draft
	gene_id_nrm = gene_id.lower()

	tpl_data = {
		"gene": "bkr:gene_" + gene_id_nrm,
		"geneId": gene_id_nrm,
		"geneAcc": gene_id,
		"condition": make_condition_uri ( condition ),
		"conditionLabel": condition,
		"conditionId": make_id ( condition, skip_non_word_chars = True ),
		"experiment": "bkr:exp_" + exp_acc,
		"experimentId": exp_acc,
		"level": tpm
	}

	print ( dedent ( rdf_tpl.format ( **tpl_data ) ) )
						
process_gxa_experiments ( print_exp_rdf )
