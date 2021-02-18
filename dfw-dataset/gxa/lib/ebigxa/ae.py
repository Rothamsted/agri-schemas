import csv, io
from sys import stdout
from urllib.request import urlopen
import requests
from textwrap import dedent

from ebigxa.utils import rdf_str, rdf_gxa_namespaces
from etltools.utils import normalize_rows_source

from ebigxa.gxa import gxa_tpm_url, gxa_dex_url
import logging

from concurrent.futures import ThreadPoolExecutor
from time import sleep

log = logging.getLogger ( __name__ )

"""
  A facility that invokes rnaseqer_experiments_download for multiple organism IDs (coming from either a 
  io.StringIO or a file) and filter them via ae_accessions_filter()
"""
def rnaseqer_experiments_download_all ( organism_id_rows_src, out = stdout ):
	rows_source = normalize_rows_source ( organism_id_rows_src )
	for organism_id in rows_source:
		log.info ( "Downloading experiments about %s", organism_id )
		this_out = io.StringIO ()
		rnaseqer_experiments_download ( organism_id, this_out )
		this_out = this_out.getvalue ()
		this_out = io.StringIO ( this_out, newline = None )
		for (exp_acc, exp_types) in ae_accessions_filter ( this_out ):
			print ( "%s\t%s" % (exp_acc, ",".join ( exp_types ) ), file = out )


"""
  Gets a plain list of EBI sequencing experiments from the RNASeq-er API (https://www.ebi.ac.uk/fg/rnaseq/api/)
  This has to be filtered to get the relevant ones (done by ae_accessions()).
  
  A list of possible values for organism_id is at https://www.ebi.ac.uk/fg/rnaseq/api/tsv/0/getOrganisms/plants
"""
def rnaseqer_experiments_download ( organism_id, out = stdout ):
	if ( not organism_id ):
		organism_list_url = "https://www.ebi.ac.uk/fg/rnaseq/api/tsv/0/getOrganisms/plants"
		raise ValueError ( "organism_id must be non-null, a list of possible values is at '%s'" % organism_list_url )
	rnaseqer_base_url = "https://www.ebi.ac.uk/fg/rnaseq/api/tsv/getStudiesByOrganism/"
	url = rnaseqer_base_url + organism_id
	with urlopen( url ) as handler:
		print ( handler.read ().decode (), file = out )


"""
  Gets a list of GXA, accessions, taking input from the output coming from rnaseqer_experiments_download().
  
  Such input is filtered by removing accessions not being in AE, or in GXA. For each accession, it's checked
  that at least one of TPM or differential expression values are available.
  
  The result is a generator yielding binary tuples, each with an accession and another list of the types available 
  for that accession (current possible values are RNASeq, DEX)
"""
def ae_accessions_filter ( rows_source ):
	rows_source = normalize_rows_source ( rows_source )		
	next ( rows_source ) # Skip the header
	
	# TODO: Initially, I've tried some parallelism, but it seems that EBI throttling makes things
	# worse. Possibly switch this back to sequential
	#
	with ThreadPoolExecutor ( 1 ) as pool:
		result = pool.map ( _acc_filter_collector, rows_source, chunksize = 50 )
		result = filter ( lambda exp_row: exp_row, result )
		return result

"""
  Filter the properties of a single experiment by checking its EBI URLs.
  Returns a tuple that correspond to one of the entries collected by ae_accessions_filter().
  
  This should be a function nested in ae_accessions_filter(), but ThreadPoolExecutor.map() doesn't allow
  that. 
"""
def _acc_filter_collector ( exp_row ):
	"""
		Tries to get experiment properties (if it has the IDF descriptor, if its RNASeq or DEX) by 
		checking known EBI URLs that correspond to those properties.
	"""
	def _get_exp_type ( exp_acc ):
		probes = [ ( "IDF", ae_magetab_url ( exp_acc, "idf" ) ) ]
		probes.append ( ( "RNASeq", gxa_tpm_url ( exp_acc ) ) )
		probes.append ( ( "DEX", gxa_dex_url ( exp_acc ) ) )
		types = [ "RNASeq", "DEX" ]
		for (utype, url) in probes:
			# TODO: I'm observing heavy EBI throttling, so, slow is betther than stuck. 
			# See also the notes in ae_accessions_filter()
			sleep ( 1 )
			hreq = requests.head ( url, stream=True )
			if hreq.status_code >= 400:
				if "IDF" == utype:
					log.debug ( "Can't download IDF file for %s, skipping", exp_acc )
					return None
			else:
				if "IDF" != utype: types.append ( utype )
		if not types:
			log.debug ( "%s hasn't downloadable expression data, skipping", exp_acc )
		return types
	exp_acc = exp_row [ 0 ]
	log.debug ( "Filtering: %s", exp_acc )
	gxa_types = _get_exp_type ( exp_acc )
	return (exp_acc, gxa_types) if gxa_types else None 
		
		
"""
	Renders the RDF for all experiments in the parameter, using rdf_ae_experiment(). 
	
	acc_rows_source is a list of accessions, achievable from ae_accessions_filter() and rnaseqer_experiments_download()
"""
def rdf_ae_experiments ( acc_rows_source, out = stdout ):
	
	print ( rdf_gxa_namespaces (), file = out )

	# Process the IDF, the MAGETAB file that describes the experiment
	for exp_row in normalize_rows_source ( acc_rows_source ):
		exp_acc = exp_row if type ( exp_row ) == str else exp_row [ 0 ]
		rdf = rdf_ae_experiment ( exp_acc )
		print ( rdf, file = out )
		

"""
  Renders the RDF about an ArrayExpress/GXA experiment, taking its description from its published
  MAGETAB (the IDF file).
  
"""
def rdf_ae_experiment ( exp_accession, specie = "" ):

	specie2terms = { 
		"arabidopsis": [ "http://purl.bioontology.org/ontology/NCBITAXON/3701" ],
		"wheat": [ "http://purl.bioontology.org/ontology/NCBITAXON/4565" ]
	}

	idf_url = ae_magetab_url ( exp_accession, "idf" )

	with urlopen ( idf_url ) as idf_stream:
		csv_reader = csv.reader ( io.TextIOWrapper ( idf_stream, encoding = 'utf-8' ), delimiter = "\t" )
		# we need to normalise keys to lower case, cause they're used inconsinstently sometimes
		idf = filter ( lambda row: len ( row ) >= 2, csv_reader ) 
		idf = { row [ 0 ].lower (): row [ 1 ] for row in idf }

		exp_acc = idf [ "comment[arrayexpressaccession]" ]
		idf [ "accession" ] = exp_acc # .format() has problems with the original key
		idf [ "experiment" ] = "bkr:exp_" + exp_acc
		exp_pmid = idf.get ( "pubmed id" ) 
		if exp_pmid: idf [ "publication" ] = "bkr:pmid_" + str ( exp_pmid )

		rdf_tpl = """
		{experiment} a bioschema:Study;
			schema:identifier "{accession}";
		"""
		rdf = dedent ( rdf_tpl.format (**idf) )

		# Facility to add IDF fields to the RDF
		# fields is a map of original field -> RDF property
		def rdf_adder ( fields ):
			rdf = ""
			for (key, rdf_prop) in fields.items ():
				rdf += rdf_str ( idf, key, "\t" + rdf_prop )
			return rdf

		rdf += rdf_adder ( { 
			"investigation title": "dc:title",
			"experiment description": "schema:description",
			"public release date": "schema:datePublished"
		})
		if exp_pmid: rdf += "\tschema:subjectOf {publication};\n".format ( **idf )

		specie_terms = specie2terms.get ( specie )
		if specie_terms:
			specie_literals = ", ".join ( [ "<" + s + ">" for s in specie_terms ] )
			rdf += "\tschema:additionalProperty " + specie_literals + ";\n"

		rdf += ".\n"

		if exp_pmid:
			rdf += "\n"
			rdf += "{publication} a agri:ScholarlyPublication;\n".format ( **idf )
			rdf += rdf_adder ({
				"publication title": "dc:title",
				"pubmed id": "agri:pmedId",
				"publication author list": "agri:authorsList"
			})
			rdf += ".\n"
		
		return rdf
	# /end: idf_stream
# /end: rdf_ae_experiment



"""
  The ArrayExpress URL of an experiment file.
  
  file_type is either 'idf' or 'sdrf'
"""
def ae_magetab_url ( exp_accession, file_type ):
	magetab_base_url = "https://www.ebi.ac.uk/arrayexpress/files/{0}/{0}.{1}.txt"
	url = magetab_base_url.format ( exp_accession, file_type )
	return url
