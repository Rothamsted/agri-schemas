import json, csv, re, io
from urllib.request import urlopen
from sys import stderr, stdin
from textwrap import dedent

from utils import make_id, get_gxa_accessions, print_rdf_namespaces

def make_condition_uri ( condition_label ):
	return "bkr:cond_" + make_id ( condition_label )

# Gets genes to be filtered from a file.
def get_knet_genes ():
	target_gene_ids = []
	with open ( "./rnd-knet-genes.txt" ) as target_f:
		target_gene_ids = [ row [ 0 ] for row in csv.reader ( target_f, delimiter = "\t", quotechar = '"' ) ]
	return list ( filter ( lambda id: "locus:" not in id, target_gene_ids ) )

	#for target_id in target_gene_ids:
	#	print ( "target: '%s'" % target_id, file = stderr )

# The URL of the TPM gene expression levels
def get_gxa_down_url ( exp_acc ):
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc \
		+ "/resources/ExperimentDownloadSupplier.RnaSeqBaseline/tpms.tsv"


"""
  Executes the processor for every GXA gene/condition found on the server.
	
	The processor has the parameters: exp_acc, gene_id, condition, tpm
	we use this for several tasks, like printing RDF, extracting the conditions
"""
def process_gxa_experiments ( exp_processor ):

	target_gene_ids = get_knet_genes()

	for exp_acc in get_gxa_accessions ():
		
		gxa_down_url = get_gxa_down_url ( exp_acc )
		print ( ">>> '%s', '%s'" % (exp_acc, gxa_down_url), file = stderr )
	
		conditions = []
		exp_levels = []
	
	  # Process the expression data row-by-row
		try:
			with urlopen ( gxa_down_url ) as gxa_stream:
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
