from textwrap import dedent

from utils import make_id, print_rdf_namespaces
from gxa_common import process_gxa_experiments, make_condition_uri

print_rdf_namespaces ()


def print_exp_rdf ( exp_acc, gene_id, condition, tpm  ):
	rdf_tpl = """
		{gene} a bioschema:Gene
		.

		{gene} a rdfs:Statement;
			agri:score "{level}";
			rdf:subject {gene};
			rdf:predicate bioschema:expressedIn;
			rdf:object {condition};
			agri:evidence {experiment}
		.
		
		{condition} a agri:StudyFactor;
			schema:prefName "{conditionLabel}"
		.
	"""

	tpl_data = {
		"gene": "bkr:gene_" + gene_id,
		"condition": make_condition_uri ( condition ),
		"conditionLabel": condition,
		"experiment": "bkr:exp_" + exp_acc,
		"level": tpm
	}

	print ( dedent ( rdf_tpl.format ( **tpl_data ) ) )
						
process_gxa_experiments ( print_exp_rdf )
