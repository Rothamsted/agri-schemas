import bz2
import csv
import io
import logging
import pathlib
import re
from sys import stdout
from textwrap import dedent
from urllib.request import urlopen

from biotools.bioportal import AgroPortalClient, BioPortalClient
from ebigxa.ae import ae_get_experiment_descriptors, make_ae_exp_uri, rdf_ae_experiment
from ebigxa.utils import rdf_gxa_namespaces
from etltools.utils import make_id, normalize_rows_source, uri2accession, js_from_file, js_to_file, BinaryWriter
from kpyutils import web


log = logging.getLogger ( __name__ )

"""
  Merges experiment descriptors from the AE API (via ae_get_experiment_descriptors()) and GXA API.
  
  It returns the JSON coming from ae_get_experiment_descriptors(), with the additional field
  gxaAnalysisType, taken from the GXA API (experimentType).
  
  AE experiments that aren't in GXA results are also filtered away from the final result. We have seen
  this happens sometimes (due delayed updates?).
"""
def gxa_get_experiment_descriptors ( organisms ):
	aejss = ae_get_experiment_descriptors ( organisms )
	result = {}
	# This is the API I found by inspecting the HTML UI, it doesn't seem to be accepting any parameter, 
	# the experiments are already organism-filtered by the AE API call.
	gxajss = web.url_get_json ( "https://www.ebi.ac.uk/gxa/json/experiments" )
	gxajss = gxajss [ "experiments" ] # Extract what we need
	gxajss = { js [ "experimentAccession" ]: js for js in gxajss }
	for exp_acc, aejs in aejss.items ():
		if exp_acc not in gxajss:
			# See above
			continue
		aejs [ "gxaAnalysisType" ] = gxajss [ exp_acc ] [ "experimentType" ]
		result [ exp_acc ] = aejs
	return result  


"""
  Wraps gxa_get_experiment_descriptors() behind a cache file, ie, 
  
  if gxa_js_file_path is present, just returns its conents, else
  invokes gxa_get_experiment_descriptors(), saves it into gxa_js_file_path and returns
  the JSON result.
  
  This is useful in Snakemake, where you can't have global variables (every rule execution
  is a new process), so you can save global states in files.
  
"""
def gxa_get_experiment_descriptors_cached ( organisms, gxa_js_file_path: str ) -> dict:
	if pathlib.Path ( gxa_js_file_path ).exists ():
		log.info ( "Loading AE/GXA descriptor from local file: '%s'", gxa_js_file_path )
		return js_from_file ( gxa_js_file_path )
	gxa_js = gxa_get_experiment_descriptors ( organisms )
	js_to_file ( gxa_js, gxa_js_file_path )
	return gxa_js


"""
  Builds all the RDF that concerns a single GXA experiment, that is: 
  
  - rdf_gxa_namespaces()
  - rdf_ae_experiment()
  - rdf_gxa_tpm_levels() or rdf_gxa_dex_levels(), depending on the experiment type
  - rdf_gxa_conditions()
  
"""
def gxa_rdf_all ( exp_js: dict, out = stdout, target_gene_ids: set = None ):
	if not out: out = io.StringIO ()
	
	print ( rdf_gxa_namespaces(), file = out )
	rdf_ae_experiment ( exp_js, out )
		
	exp_acc = exp_js [ 'accession' ]
	ae_tech_type = exp_js [ "aeTechnologyType" ]
	gxa_analysis_type = exp_js [ 'gxaAnalysisType' ]
	cond_labels = set()
	
	if "Baseline" == gxa_analysis_type:
		rdf_gxa_tpm_levels ( exp_acc, out, cond_labels, target_gene_ids )
	else:
		rdf_gxa_dex_levels ( exp_acc, ae_tech_type, out, cond_labels, target_gene_ids )

	rdf_gxa_conditions ( cond_labels, out )

	if ( type ( out ) == io.StringIO ): return out.getvalue()

"""
	Saves gxa_rdf_all() to a file.
"""
def gxa_rdf_all_save ( exp_js, file_path: str, target_gene_ids = None, compress = False ):
	out = open ( file_path, mode = "w" ) if not compress \
				else BinaryWriter ( bz2.open ( file_path, "w" ) )
	try:
		gxa_rdf_all ( exp_js, out, target_gene_ids )
	finally:
		out.close ()
	

"""
  Yields the RDF for the TPM levels of a baseline experiment.
  
  condition_labels is used to accumulate labels coming from the conditions in which genes are expressed.
  This is to be passed to rdf_gxa_conditions().
  
  target_gene_ids is a set of ENSEMBL gene identifiers, to be used for consider only a subset of genes
  (used mostly for unit tests).
  
  out is passed to print ()'s file parameter, ie, it's the destination stream. If set to None explicitly,
  a string is generated and returned (WARNING: might be very big).  
"""
def rdf_gxa_tpm_levels ( exp_acc: str, out = stdout, condition_labels: set = None, target_gene_ids: set = None ):

	def rdf_level ( gene_id, condition_label, tpm, ordinal_tpm ):
		# TODO: it would be more correct to not change the case, but we want Knet compatibility
		exp_uri = make_ae_exp_uri ( exp_acc )
		gene_id_nrm = gene_id.lower()
		gene_uri = make_gene_uri ( gene_id )
		cond_id = make_id ( condition_label, skip_non_word_chars = False )
		cond_uri = make_condition_uri ( condition_label )
	
		rdf = f"""
			bkr:gxaexp_{exp_acc}_{gene_id_nrm}_{cond_id} a rdf:Statement;
				agri:tpmCount {tpm};
				agri:ordinalTpm "{ordinal_tpm}";
				rdf:subject {gene_uri};
				rdf:predicate bioschema:expressedIn;
				rdf:object {cond_uri};
				agri:evidence {exp_uri}
			.
				
			{gene_uri} bioschema:expressedIn {cond_uri}.
		"""
		rdf = dedent ( rdf )
	
		print ( rdf, file = out )
						
	if not out: out = io.StringIO ()
						
	tpm_url = gxa_tpm_url ( exp_acc )
	log.info ( "Downloading GXA TPM levels from '%s'", exp_acc )
	log.debug ( "Downloading URL: '%s'", tpm_url )
	
	# Process the expression data row-by-row
	condition_cols = []
	is_on_headers = True
	with urlopen ( tpm_url ) as gxa_stream:
		for row in csv.reader ( io.TextIOWrapper ( gxa_stream, encoding = 'utf-8' ), delimiter = "\t" ):
			# First rows are headers, up to the table's headers, which start with "Gene ID"
			if is_on_headers:
				if len( row ) > 0 and row [ 0 ] == "Gene ID":
					# Condition labels are in the headers
					condition_cols = row [ 2: ]
					log.debug ( "Conditions: %s", condition_cols )
					is_on_headers = False # since now on
				continue # start reading data after the last header

			gene_id = row [ 0 ].upper()
			if target_gene_ids and gene_id not in target_gene_ids:
				# log.debug ( "Skipping non-target gene: '%s'", gene_id )
				continue
			
			gene_has_levels = False
			exp_levels = row[ 2: ]
			for j in range ( len ( exp_levels ) ):
				tpm = exp_levels [ j ]
				ordinal_tpm = get_ordinal_tpm ( tpm, gene_id )
				if not ordinal_tpm: continue
				rdf_level ( gene_id, condition_cols [ j ], tpm, ordinal_tpm )
				# We add it here so that only those that are actually used are returned
				condition_labels.add ( condition_cols [ j ] )
				gene_has_levels = True
			# /end: column loop
				
			if not gene_has_levels: continue
			gene_name = row [ 1 ]
			rdf_gene ( gene_id, gene_name, out )
		# /end: experiment results loop
	# /end: experiment results stream
	if is_on_headers:
		log.warning ( "Didn't see any data in the experiment " + exp_acc )
		
	if ( type ( out ) == io.StringIO ): return out.getvalue()
#/end: rdf_gxa_tpm_levels



_dex_condre = "'([^']+)'"
_dex_score_type_re = "\s*\.(foldChange|pValue)"
# this includes the optional case: "'salicylic acid; 0.5 millimolar' vs 'none' in 'wild type genotype' .foldChange"
DEX_COND_PATTERN = re.compile ( f"{_dex_condre} vs {_dex_condre}( in {_dex_condre})?{_dex_score_type_re}" )
DEX_COND_TIME_PATTERN = re.compile ( f"(.+) at '([0-9]+) hour'{_dex_score_type_re}")

"""
  Yields the RDF for the TPM levels of a baseline experiment.

	Parameters are the same as rdf_gxa_dex_levels()  
"""
def rdf_gxa_dex_levels ( 
	exp_acc: str, technology_type: str, out = stdout, 
	condition_labels: set = None, target_gene_ids: set = None ):
	
	# Gets the condition mentioned by a header. See below for details. 
	def get_conditions ( conds_header: str ):
		if not conds_header: return {}
		conds_header = conds_header.strip ()
		if not conds_header: return {}
		
		result = {}

		# Might be: 'cond' vs 'baseline' at 'h hours'
		# the time point is optional
		
		# So, let's see if we have a time to extract 
		time_match = DEX_COND_TIME_PATTERN.match ( conds_header )
		if time_match:
			# TODO: can it be different than hours?
			result [ 'time' ] = int ( time_match.group ( 2 ) )
			# Done, cut away the time part and reduce it to the timeless case
			conds_header = time_match.group ( 1 ) + "." + time_match.group ( 3 )
				
		# Now match only cond/baseline
		cond_match = DEX_COND_PATTERN.match ( conds_header )
		if not cond_match: return {}
		
		# At the end, all the details are in a dictionary  		
		result [ 'baseline' ] = cond_match.group ( 2 )
		result [ 'condition' ] = cond_match.group ( 1 )
		# This is an optional part looking like "in 'wildtype'"
		in_clause = cond_match.group ( 4 )
		if in_clause: result [ 'baselineExt' ] = in_clause
		result [ 'scoreType' ] = cond_match.group ( 5 )

		return result

	def rdf_level ( gene_id, condition_label, base_condition_label, ext_base_condition_label, fold_change, pvalue, time_point ):
		# TODO: it would be more correct to not change the case, but we want Knet compatibility
		exp_uri = make_ae_exp_uri ( exp_acc )
		gene_id_nrm = gene_id.lower()
		gene_uri = make_gene_uri ( gene_id )
		
		cond_id = make_id ( condition_label, skip_non_word_chars = False )
		cond_uri = make_condition_uri ( condition_label )

		base_cond_id = make_id ( base_condition_label, skip_non_word_chars = False )
		base_cond_uri = make_condition_uri ( base_condition_label )

		ext_base_cond_id, ext_base_cond_uri = None, None
		if ext_base_condition_label:
			ext_base_cond_id = make_id ( ext_base_condition_label, skip_non_word_chars = False )
			ext_base_cond_uri = make_condition_uri ( ext_base_condition_label )
	
	
		exp_stmt_uri = f"bkr:gxaexp_{exp_acc}_{gene_id_nrm}_{cond_id}_vs_{base_cond_id}"
		if ext_base_cond_uri:
			exp_stmt_uri += f"_in_{ext_base_cond_id}"
			
		if time_point != -1: exp_stmt_uri += f"_{time_point}h"
	
		rdf = f"""
			{exp_stmt_uri} a rdf:Statement;
				rdf:subject {gene_uri};
				rdf:predicate bioschema:expressedIn;
				rdf:object {cond_uri};
				agri:baseCondition {base_cond_uri};
				agri:log2FoldChange {fold_change};
				agri:pvalue {pvalue};
				agri:evidence {exp_uri}
			.
				
			{gene_uri} bioschema:expressedIn {cond_uri}.
		"""

		rdf = dedent ( rdf )
		
		if ext_base_cond_uri:
			rdf += f"\n{exp_stmt_uri} agri:baseCondition {ext_base_cond_uri}.\n"

			
		if time_point != -1:
			time_point_str = str ( time_point ) + " hours"
			time_point_uri = make_condition_uri ( time_point_str )
			rdf+= f"\n{exp_stmt_uri} agri:timePoint {time_point_uri}."
			
		print ( rdf, file = out )
						
	if not out: out = io.StringIO ()
						
	dex_url = gxa_dex_url ( exp_acc, technology_type )
	log.info ( "Downloading GXA DEX levels from '%s'", exp_acc )
	log.debug ( "Downloading URL: '%s'", dex_url )
	
	# Process the expression data row-by-row
	# They have the same format except for an extra-column reporting the array probe set
	cond_start_idx = 3 if technology_type == "Microarray" else 2 
	cond_details = {}
	is_on_headers = True
	with urlopen ( dex_url ) as gxa_stream:
		for row in csv.reader ( io.TextIOWrapper ( gxa_stream, encoding = 'utf-8' ), delimiter = "\t" ):
			# First rows are headers, up to the table's headers, which start with "Gene ID"
			if is_on_headers:
				if len( row ) > 0 and row [ 0 ] == "Gene ID":
					# Condition labels are in the headers, let's collect them and let's extract their structure
					for j in range ( cond_start_idx, len ( row ) ):
						cond_col = row [ j ]
						cond_detail = get_conditions ( cond_col )
						if not cond_detail: continue
						cond_details [ j ] = cond_detail
					if not cond_details: break # We don't have valid columns 
					is_on_headers = False # since now on
				continue # start reading data after the last header
	
			gene_id = row [ 0 ].upper()
			if target_gene_ids and gene_id not in target_gene_ids:
				# log.debug ( "Skipping non-target gene: '%s'", gene_id )
				continue
		
			all_levels = {} # time point -> details, or -1 => details without time point
			for j, cond_detail in cond_details.items ():
				time = cond_detail.get ( "time", -1 )
				
				# it's updated from multiple columns by multiple iterations in this loop 
				levels = all_levels.get ( time, {} ) 
				
				level_value = row [ j ]
				if not level_value: continue
				level_value = float ( level_value )
				
				if cond_detail [ "scoreType" ] == 'foldChange':
					levels [ "foldChange" ] = level_value
				else: 
					levels [ "pvalue" ] = level_value
				
				levels [ "condition" ] = cond_detail [ "condition" ]
				levels [ "baseline" ] = cond_detail [ "baseline" ]
				levels [ "baselineExt" ] = cond_detail.get ( "baselineExt", None )

				all_levels [ time ] = levels
			#/end: loop on condition columns

			# OK, we have the values structured as we want, see if they're good enough
			gene_has_levels = False
			for time_point, levels in all_levels.items ():
				fold_change = levels.get ( "foldChange", 0 )
				if abs ( fold_change ) < 1: 
					#log.debug ( "Skipping low/absent fold change for gene %s", gene_id )
					continue
				
				pvalue = levels.get ( "pvalue", 1 )
				if pvalue > 0.05:
					#log.debug ( "Skipping low/absent p-value for gene %s", gene_id )
					continue								

				condition = levels [ "condition" ]
				baseline = levels [ "baseline" ]
				baseline_ext = levels [ "baselineExt" ]

				rdf_level ( gene_id, condition, baseline, baseline_ext, fold_change, pvalue, time_point )

				condition_labels.add ( condition )
				condition_labels.add ( baseline )
				if baseline_ext: condition_labels.add ( baseline_ext )
				
				if time != -1: condition_labels.add ( str ( time ) + " hours" )
				gene_has_levels = True
			#/end: loop all_levels
			
			if not gene_has_levels: continue
			gene_name = row [ 1 ]
			rdf_gene ( gene_id, gene_name, out )
			
		# /end: experiment results loop
	# /end: experiment results stream
	if is_on_headers:
		log.warning ( "Didn't see any data in the experiment " + exp_acc )
		
	if ( type ( out ) == io.StringIO ): return out.getvalue()
#/end: rdf_gxa_dex_levels






"""
  Convert gene information fetched from TPM/DEX levels into agrischema RDF.
  
	out is passed to print ()'s file parameter, ie, it's the destination stream. If set to None explicitly,
	a string is generated and returned.  
"""
def rdf_gene ( gene_id: str, gene_name: str, out = stdout ):
	if not out: out = io.StringIO ()
	
	gene_uri = make_gene_uri ( gene_id )

	rdf = f"""
		{gene_uri} a bioschema:Gene;
			schema:identifier "{gene_id}";
		.
	"""
	rdf = dedent ( rdf )
	print ( rdf, file = out )
	
	if gene_name and gene_name.lower () != gene_id.lower ():
		# we use rdfs:label for the name cause we're not so sure if it's a pref or alt name  
		print ( f"\n{gene_uri} rdfs:label \"{gene_name}\".\n", file = out )
		
	if ( type ( out ) == io.StringIO ): return out.getvalue()	


"""
	Converts condition labels coming from GXA into RDF/agrischemas, using the agroportal text annotator to 
	map labels to common ontologies.
	
	out is passed to print ()'s file parameter, ie, it's the destination stream. If set to None explicitly,
	a string is generated and returned (WARNING: might be very big).		
"""
COND_TIME_POINT_RE = re.compile ( "([0-9]+) hours" )
def rdf_gxa_conditions ( condition_labels_rows_src, out = stdout ):
		
	if not out: out = io.StringIO ()
	
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
		
		rdf = f"""
			{cond_uri} a agri:StudyFactor;
				schema:name "{cond_label}"
			.
		"""
		rdf = dedent ( rdf )
		
		tp_match = COND_TIME_POINT_RE.match ( cond_label )
		if tp_match:
			tp_hours = int ( tp_match.group ( 1 ) )
			rdf += f"\n{cond_uri} schema:value {tp_hours}; schema:unitText \"hours\".\n"
		
		print ( rdf, file = out )
		
		onto_terms = []
		try:
			onto_terms = annotate_condition ( cond_label )
		except Exception as ex:
			log.debug ( "Error while fetching ontology annotations for '%s': %s", cond_label, str (ex) )
			has_errors = True
				
		for term in onto_terms:
			
			term_uri = term [ "uri" ]
			print ( "\n%s dc:type <%s>." % ( cond_uri, term_uri ), file = out )
			
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
		#/end: for onto_terms
	#/end: for cond_label
	if has_errors:
		log.error ( "The gene expression conditions annotation has had some errors, probably some terms weren't annotated" )
	if ( type ( out ) == io.StringIO ): return out.getvalue()	
#/end: rdf_gxa_conditions	


"""
  Annotates a condition string with ontology terms from AgroLD, using their Annotator service.
  
  You can switch to the alternative BioPortal text annotator, in both cases, a suitable set 
  of ontologies is passed to the respective API. This annotator option was introduced due to 
  periodical AgroPortal instability.
  
  When this parameter isn't specified, it is taken from
  the global/static annotate_condition.default_annotator, which you can use to set a global default
  at the begin of your application/process.
"""
def annotate_condition ( cond_label: str, annotator = None ) -> str:
	ap = None
	opts = {
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
	
	if not annotator: annotator = annotate_condition.default_annotator
	
	if annotator == "AgroPortal": 
		ap = AgroPortalClient ()
		opts [ "ontologies" ] = "CO_330,CO_321,TO,CO_121,AFO,EO,AEO,NCBITAXON,AGROVOC,FOODON"
	else:
		ap = BioPortalClient ()
		opts [ "ontologies" ] = "PO,CO-WHEAT,CO,NCBITAXON,PAE,PDO_CAS,PEAO,PPO,PTO,CPGA,FOODON"

	terms = ap.annotator_terms ( cond_label, cutoff = 5, **opts )
	return terms

annotate_condition.default_annotator = "AgroPortal"


# Gets genes to be filtered from a file or other row source.
# If the param is null, returns an empty set.
# All are converted to upper case, to make a case-insensitive match.
#
def load_filtered_genes ( gene_filter_row_src = None ) -> set:
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
def gxa_tpm_url ( exp_acc: str ) -> str: 
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc \
		+ "/resources/ExperimentDownloadSupplier.RnaSeqBaseline/tpms.tsv"
	
# The URL of the document returning the differential gene expression levels for the experiment accession
def gxa_dex_url ( exp_acc, technology_type ):
	tech_selector = "Microarray/query-results" if technology_type == "Microarray" else "RnaSeqDifferential/tsv"
	return \
		"https://www.ebi.ac.uk/gxa/experiments-content/" + exp_acc +\
		"/resources/ExperimentDownloadSupplier." + tech_selector		
		
def make_gene_uri ( gene_id: str ) -> str:
	return "bkr:gene_" + gene_id.lower()
		
def make_condition_uri ( condition_label: str ) -> str:
	return "bkr:cond_" + make_id ( condition_label, skip_non_word_chars = False )
				
"""
  Turns a TPM count into ordinal values 'low'/'medium'/'high'. This is based on the thresholds used by
  the GXA (https://www.ebi.ac.uk/gxa/FAQ.html).
  
  The gene_id is used for logging invalid or too low TPMs. 
"""
def get_ordinal_tpm ( tpm: float, gene_id: str = None ) -> str:
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
