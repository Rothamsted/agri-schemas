import csv, io
from sys import stdout, stderr
from urllib.request import urlopen
import requests
from textwrap import dedent

from ebigxa.utils import rdf_str, rdf_gxa_namespaces
from etltools.utils import normalize_rows_source

from ebigxa.gxa import gxa_tpm_url


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
		print ( handler.read (), file = out )


"""
  Gets a list of GXA, accessions, taking input from the output coming from rnaseqer_experiments_download().
  
  Such input is filtered by removing accessions not being in AE, or in GXA (for each accession, it's checked
  that at least TPM or differential expression values ara available).
"""
def ae_accessions_filter ( rows_source ):
	def is_valid_for_us ( exp_acc ):
		probes = ( ( "AE/IDF", ae_magetab_url ( exp_acc, "idf" ) ) )
		probes.append ( "GXA/TPM", gxa_tpm_url ( exp_acc ) )
		for (utype, url) in probes:
			hreq = requests.get ( url )
			if not hreq:
				print ( "Can't download " + utype + " file for " + exp_acc + ", skipping", file = stderr )
				return False
		return True
		
	rows_source = normalize_rows_source ( rows_source )
	next ( rows_source ) # Skip the header
	for row in rows_source:
		exp_acc = row [ 0 ]
		if is_valid_for_us ( exp_acc ): yield exp_acc
		
		
"""
	Renders the RDF for all experiments in the parameter, using rdf_ae_experiment(). 
	
	acc_rows_source is a list of accessions, achievable from ae_accessions_filter() and rnaseqer_experiments_download()
"""
def rdf_ae_experiments ( acc_rows_source, out = stdout ):
	
	print ( rdf_gxa_namespaces (), file = out )

	# Process the IDF, the MAGETAB file that describes the experiment
	for exp_acc in normalize_rows_source ( acc_rows_source ):
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
		idf = { row [ 0 ].lower (): row [ 1 ] for row in csv_reader }

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
