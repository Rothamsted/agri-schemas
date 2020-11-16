import csv, io
import os.path
from urllib.request import urlopen
from sys import stderr, stdout
from textwrap import dedent

from ebigxa.utils import rdf_gxa_namespaces
from etltools.utils import make_id, normalize_rows_source

def rdf_gxa_tpm_levels ( gxa_accs_rows_src, out = stdout, filtered_genes_path = None ):
	def rdf_gxa_tpm_level_processor ( exp_acc, gene_id, condition, tpm ):
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
	
		print ( dedent ( rdf_tpl.format ( **tpl_data ) ), file = out )
			
	print ( rdf_gxa_namespaces (), file = out )			
	_process_gxa_tpm_levels ( gxa_accs_rows_src, rdf_gxa_tpm_level_processor, filtered_genes_path )



# ----------------------- ----------------------- ----------------------- ----------------------- 


"""
  Executes the processor for every GXA gene/condition found on the server.
	
	The processor has the parameters: exp_acc, gene_id, condition, tpm
	we use this for several tasks, like printing RDF, extracting the conditions
"""
def _process_gxa_tpm_levels ( gxa_rows_src, exp_processor, filtered_genes_path ):

	target_gene_ids = load_filtered_genes ( filtered_genes_path )

	for exp_acc in normalize_rows_source ( gxa_rows_src ):
		
		tpm_url = gxa_tpm_url ( exp_acc )
		print ( ">>> '%s', '%s'" % (exp_acc, tpm_url), file = stderr )
	
		conditions = []
		exp_levels = []
	
		# Process the expression data row-by-row
		try:
			with urlopen ( tpm_url ) as gxa_stream:
				for row in csv.reader ( io.TextIOWrapper ( gxa_stream, encoding = 'utf-8' ), delimiter = "\t" ):
					if not conditions:
						# Conditions are in the headers
						conditions = row [ 2: ]
						print ( "conditions: %s" % conditions, file = stderr )
						print ( "target_gene_ids has %d IDs" % len ( target_gene_ids ), file = stderr )
						continue
	
					gene_id = row [ 0 ].upper()
					if not ( gene_id in target_gene_ids ):
						print ( "Skipping non-target gene: '%s'" % gene_id, file = stderr )
						continue
	
					exp_levels = row[ 2: ]
					for j in range ( len ( exp_levels ) ):
						tpm = exp_levels [ j ]
						if not tpm:
							print ( "Skipping empty-count gene: %s" % gene_id, file = stderr )
							continue
						tpm = float ( tpm )
						# Convert to null/low/medium/high
						if tpm <= 0.5:
							print ( "Skipping low-count (%d) gene: %s" % ( tpm, gene_id ), file = stderr )
							continue
						if tpm <= 10: 
							tpm = 'low'
						elif tpm <= 1000:
							tpm = 'medium'
						else:
							# > 1000
							tpm = 'high'
	
						exp_processor ( exp_acc, gene_id, conditions [ j ], tpm )

					# /end: column loop
				# /end: experiment results loop
			# /end: experiment results stream
		except FileNotFoundError as ex:
			print ( "Error: %s" % str (ex), file = stderr )
			continue
	# /end: experiment loop
# /end:process_gxa_experiments


# Gets genes to be filtered from a file.
# If the param is null, returns an empty set
#
def load_filtered_genes ( file_path = None ):
	if not file_path: return set ()
	if not os.path.isfile ( file_path ):
		print ( "Filter genes file '%s' not found, skipping", file = stderr )
		return set ()
	with open ( file_path ) as target_f:
		target_gene_ids = ( row [ 0 ] for row in csv.reader ( target_f, delimiter = "\t", quotechar = '"' ) )
		# We sometimes have this in Knetminer
		target_gene_ids = filter ( lambda gid: "locus:" not in gid, target_gene_ids )
		
		result = set ()
		for gid in target_gene_ids: result.add ( gid )
		return result

# The URL of the TPM gene expression levels
def gxa_tpm_url ( exp_acc ):
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc \
		+ "/resources/ExperimentDownloadSupplier.RnaSeqBaseline/tpms.tsv"

def make_condition_uri ( condition_label ):
	return "bkr:cond_" + make_id ( condition_label, skip_non_word_chars = True )
