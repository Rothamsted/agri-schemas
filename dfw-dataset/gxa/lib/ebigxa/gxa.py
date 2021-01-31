import csv, io
import logging
from urllib.request import urlopen
from sys import stdout
from textwrap import dedent

from ebigxa.utils import rdf_gxa_namespaces
from etltools.utils import make_id, uri2accession, normalize_rows_source
from biotools.bioportal import AgroPortalClient

import re


log = logging.getLogger ( __name__ )

"""
  Converts the TPM levels for GXA accessions into RDF/agrischemas. 
  
  It also returns a set of condition labels, which can be used with rdf_gxa_conditions(), or
  etl.utils.dump_rows().
"""
def rdf_gxa_tpm_levels ( gxa_accs_rows_src, out = stdout, filtered_genes_path = None ):
	condition_labels = set ()
	def rdf_gxa_tpm_level_processor ( exp_acc, gene_id, condition, tpm, ordinal_tpm ):
		rdf_tpl = """
			{gene} a bioschema:Gene;
				schema:identifier "{geneAcc}";
			.
	
			bkr:gxaexp_{experimentId}_{geneId}_{conditionId} a rdfs:Statement;
				agri:tpmCount {tpm};
				agri:ordinalTpm "{ordinalTpm}";
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
			"conditionId": make_id ( condition, skip_non_word_chars = False ),
			"experiment": "bkr:exp_" + exp_acc,
			"experimentId": exp_acc,
			"tpm": tpm,
			"ordinalTpm": ordinal_tpm
		}
	
		print ( dedent ( rdf_tpl.format ( **tpl_data ) ), file = out )
		condition_labels.add ( condition )
			
	print ( rdf_gxa_namespaces (), file = out )			
	process_gxa_tpm_levels ( gxa_accs_rows_src, rdf_gxa_tpm_level_processor, filtered_genes_path )
	return condition_labels



"""
  Executes the processor for every GXA gene/condition found on the server.
	
	The processor has the parameters: exp_acc, gene_id, condition, tpm
	we use this for several tasks, like printing RDF, extracting the conditions
"""
def process_gxa_tpm_levels ( gxa_rows_src, exp_processor, gene_filter_row_src ):
	target_gene_ids = load_filtered_genes ( gene_filter_row_src )
	
	if target_gene_ids: log.debug ( "target_gene_ids has %d IDs", len ( target_gene_ids ) )

	for exp_acc in normalize_rows_source ( gxa_rows_src ):
		
		tpm_url = gxa_tpm_url ( exp_acc )
		log.info ( "Downloading GXA TPM levels from '%s'", exp_acc )
		log.debug ( "Downloading URL: '%s'", tpm_url )
		
		# Process the expression data row-by-row
		conditions = []
		is_on_headers = True
		try:
			with urlopen ( tpm_url ) as gxa_stream:
				for row in csv.reader ( io.TextIOWrapper ( gxa_stream, encoding = 'utf-8' ), delimiter = "\t" ):
					# First rows are headers, up to the table's headers, which start with "Gene ID"
					if is_on_headers:
						if len( row ) > 0 and row [ 0 ] == "Gene ID":
							# Condition labels are in the headers
							conditions = row [ 2: ]
							log.debug ( "Conditions: %s", conditions )
							is_on_headers = False # since now on
						continue # start reading data after the last header
	
					gene_id = row [ 0 ].upper()
					if target_gene_ids and gene_id not in target_gene_ids:
						# log.debug ( "Skipping non-target gene: '%s'", gene_id )
						continue
	
					exp_levels = row[ 2: ]
					for j in range ( len ( exp_levels ) ):
						tpm = exp_levels [ j ]
						ordinal_tpm = get_ordinal_tpm ( tpm, gene_id )
						if not ordinal_tpm: continue
						exp_processor ( exp_acc, gene_id, conditions [ j ], tpm, ordinal_tpm )
					# /end: column loop
				# /end: experiment results loop
			# /end: experiment results stream
		except FileNotFoundError as ex:
			log.exception ( "Error: while processing experiment '%s': %s, skipping the experiment", str (ex) )
			continue
		if is_on_headers:
			log.warning ( "Didn't see any data in the experiment " + exp_acc )
	# /end: experiment loop
# /end:process_gxa_tpm_levels


"""
  Turns a TPM count into ordinal values 'low'/'medium'/'high'. This is based on the thresholds used by
  the GXA (https://www.ebi.ac.uk/gxa/FAQ.html).
  
  The gene_id is used for logging invalid or too low TPMs. 
"""
def get_ordinal_tpm ( tpm, gene_id = None ):
	if not tpm:
		# if gene_id: log.debug ( "Skipping empty TPM count for gene: %s", gene_id )
		return None
	tpm = float ( tpm )

	if tpm <= 0.5:
		# if gene_id: log.debug ( "Skipping low TPM count (%d) for gene: %s", tpm, gene_id )
		return None

	if tpm <= 10: return 'low'
	if tpm <= 1000: return 'medium'
	return 'high'	# > 1000



"""
	Converts condition labels coming from GXA into RDF/agrischemas, using the agroportal text annotator to 
	map labels to common ontologies.
"""
def rdf_gxa_conditions ( condition_labels_rows_src, out = stdout ):
	
	print ( rdf_gxa_namespaces (), file = out )			
	
	# TODO: complete!
	knet_prefixes = {
	  "TO": "http://knetminer.org/data/rdf/resources/trait_",
	  "PO": "http://knetminer.org/data/rdf/resources/plantontologyterm_"	
	}
	
	# Now, take the collected conditions and build onto-term annotations
	#
	has_errors = False
	for cond_label in normalize_rows_source ( condition_labels_rows_src ):
		cond_uri = make_condition_uri ( cond_label )
		
		onto_terms = []
		try:
			onto_terms = annotate_condition ( cond_label )
		except Exception as ex:
			log.debug ( "Error while fetching ontology annotations for '%s': %s", cond_label, str (ex) )
			has_errors = True
				
		for term in onto_terms:
			
			term_uri = term [ "uri" ]
			print ( "%s dc:type <%s>." % ( cond_uri, term_uri ), file = out )
			
			# Add the label, if any
			label = term [ "label" ]
			if label:
				print ( "<%s> schema:name \"%s\"." % ( term_uri, label ), file = out )
				
			
			# Add the accession
			acc = uri2accession ( term_uri )
			if not acc: continue
	
			print ( "<%s> schema:identifier \"%s\"." % ( term_uri, acc ), file = out )
	
			# Add links to Knetminer
			if not acc [ 2 ] == '_': continue
			acc_id = acc [ 3: ]
			if not ( acc_id and acc_id.isdigit() ): continue
			onto_id = acc [ 0: 2 ]
			if not onto_id in knet_prefixes: continue
			knet_uri = knet_prefixes [ onto_id ] + acc.lower()
			print ( "%s dc:type <%s>." % ( cond_uri, knet_uri ), file = out )
			print ( "<%s> schema:sameAs <%s>." % ( knet_uri, term_uri ), file = out )
		print ( file = out )
	#/end: for cond_label
	if not has_errors: return
	log.error ( "The gene expresion conditions annotation has had some errors, probably some terms weren't annotated" )
#/end: rdf_gxa_conditions	



# Gets genes to be filtered from a file.
# If the param is null, returns an empty set.
# All are converted to upper case, to make a case-insensitive match.
#
def load_filtered_genes ( gene_filter_row_src = None ):
	if not gene_filter_row_src: return set ()
	result = set ()
	for gene_id in normalize_rows_source ( gene_filter_row_src ):
		if not gene_id: continue
		if gene_id [ 0 ] == '#': continue
		# We sometimes have this in Knetminer and they don't work with GXA
		if "locus:" in gene_id: continue
		result.add ( gene_id.upper () )
	
	return result

# The URL of the document returning the TPM gene expression levels for the experiment accession
def gxa_tpm_url ( exp_acc ):
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc \
		+ "/resources/ExperimentDownloadSupplier.RnaSeqBaseline/tpms.tsv"

def make_condition_uri ( condition_label ):
	return "bkr:cond_" + make_id ( condition_label, skip_non_word_chars = False )

"""
  Annotates a condition string with ontology terms from AgroLD, using their Annotator service.
"""
def annotate_condition ( cond_label ):
	ap = AgroPortalClient ()
	opts = {
		"ontologies": "CO_330,CO_321,TO,CO_121,AFO,EO,AEO,NCBITAXON,AGROVOC,FOODON", 
		"longest_only": "true",
		"exclude_numbers": "false",
		"whole_word_only": "true",
		"exclude_synonyms": "false",
	  "expand_mappings": "false",
	  "fast_context": "false",
	  "certainty": "false",
	  "temporality": "false",
	  "experiencer": "false",
	  "negation": "false",
	  "score": "cvalue"			
	}
	terms = ap.annotator_terms ( cond_label, cutoff = 5, **opts )
	return terms
	

"""
	TODO: comment me!
"""
_condre = "'([^']+)'"
DEX_COND_PATTERN = re.compile ( f"{_condre} vs {_condre}\s*\.(foldChange|pValue)" )
def process_gxa_dex_levels ( gxa_rows_src, exp_processor, gene_filter_row_src ):
	
	def get_conditions ( conds_header ):
		if not conds_header: return ()
		conds_header = conds_header.strip ()
		if not conds_header: return ()
		cond_match = DEX_COND_PATTERN.match ( conds_header )
		if not cond_match: return ()
		return ( cond_match.get ( 0 ), cond_match ( 1 ) )
	
	target_gene_ids = load_filtered_genes ( gene_filter_row_src )
	
	if target_gene_ids: log.debug ( "target_gene_ids has %d IDs", len ( target_gene_ids ) )

	for exp_acc in normalize_rows_source ( gxa_rows_src ):
		
		dex_url = gxa_dex_url ( exp_acc )
		log.info ( "Downloading GXA DEG levels from '%s'", exp_acc )
		log.debug ( "Downloading URL: '%s'", dex_url )
		
		# Process the expression data row-by-row
		conditions = set()
		is_on_headers = True
		try:
			with urlopen ( dex_url ) as gxa_stream:
				for row in csv.reader ( io.TextIOWrapper ( gxa_stream, encoding = 'utf-8' ), delimiter = "\t" ):
					# First rows are headers, up to the table's headers, which start with "Gene ID"
					if is_on_headers:
						if len( row ) > 0 and row [ 0 ] == "Gene ID":
							# Condition labels are in the headers
							conds_row = row [ 2: ]
							for conds_header in conds_row:
								conds = get_conditions ( conds_header )
								if not conds:
									raise ValueError ( "Bad condition headers for the DXA levels file %s, ignoring this" % exp_acc )
								conditions.add ( conds [ 0 ] )
								conditions.add ( conds [ 1 ] )
							log.debug ( "Conditions: %s", conditions )
							is_on_headers = False # since now on
						continue # start reading data after the last header
	
					gene_id = row [ 0 ].upper()
					if target_gene_ids and gene_id not in target_gene_ids:
						# log.debug ( "Skipping non-target gene: '%s'", gene_id )
						continue
	
					exp_levels = row[ 2: ]
					j = 0
					while j < len ( exp_levels ):
						# TODO: 
						# FC = value in j, if not good, skip
						# pval = value in ++j, if not good, skip
						# extract fact/base/type conditions from the header
						# call exp_processor ( fact_cond, base_cond, FC, pval )
						pass

					# /end: column loop
				# /end: experiment results loop
			# /end: experiment results stream
		except FileNotFoundError as ex:
			log.exception ( "Error: while processing experiment '%s': %s, skipping the experiment", str (ex) )
			continue
		if is_on_headers:
			log.warning ( "Didn't see any data in the experiment " + exp_acc )
	# /end: experiment loop
# /end:process_gxa_dex_levels



# The URL of the document returning the differential gene expression levels for the experiment accession
def gxa_dex_url ( exp_acc ):
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc +\
		"/resources/ExperimentDownloadSupplier.RnaSeqDifferential/tsv"		
