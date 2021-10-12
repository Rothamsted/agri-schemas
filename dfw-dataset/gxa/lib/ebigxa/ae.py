import logging
from sys import stdout
from textwrap import dedent

from etltools.utils import rdf_str, rdf_pval, make_id, hash_generator
from kpyutils import web


log = logging.getLogger ( __name__ )


"""
	Gets ArrayExpress experiment descriptors, using the AE API.
	
	You can pass either a single string or a generator.

	A dictionary is returned such that the keys are experiment accessions and the values
	are dictionaries corresponding to the JSON objects that AE gives us.
	
	The gxa=true flag is used, cause we are interested in them only.
	TODO: this flag is currently not used, see below
"""
def ae_get_experiment_descriptors ( organisms ) -> dict:
	def get_one_organism ( organism, result = {} ) -> dict:
		log.info ( "Getting AE descriptors about %s", organism )
		url = "https://www.ebi.ac.uk/arrayexpress/json/v3/experiments?"
				
		url += web.url_param ( "species", '"' + organism + '"' )
		
		url += web.url_param_append ( "gxa", "true" )

		aejs = web.url_get_json ( url )
		aejs = aejs.get ( "experiments", {} ) # Extract what we need
		aejs = aejs.get ( "experiment", None )
		
		if not aejs:
			log.warning ( "No AE/GXA experiment found for '%s'", organism )
			return {}
		
		for js in aejs:
			ae_type = js.get ( "experimenttype", None )
			
			# Sometimes it is missing, so let's skip it
			if not ae_type: continue

			js [ "aeTechnologyType" ] = "Microarray" \
				if "transcription profiling by array" in ae_type \
				else "RNASeq"
			result [ js [ "accession" ] ] = js
		
		return result

	if type ( organisms ) == str: organisms = [ organisms ]
	result = {}
	for organism in organisms:
		get_one_organism ( organism, result )
	return result


"""
	Renders the RDF about an ArrayExpress/GXA experiment, taking its description from the JSON returned
	by the AE API, ie, ae_get_experiment_descriptors.
	
	out is passed to print ()'s file parameter, ie, it's the destination stream. If set to None explicitly,
	a string is generated and returned.	
"""
def rdf_ae_experiment ( exp_js: dict, out = stdout ) -> str:

	specie2terms = { 
		"arabidopsis thaliana": [ "http://purl.bioontology.org/ontology/NCBITAXON/3701" ],
		"triticum aestivum": [ "http://purl.bioontology.org/ontology/NCBITAXON/4565" ]
	}

	def rdf_specie ( exp_uri:str, specie_label:str ):
		if not specie_label: return ""
		specie_uri = "bkr:specie_" + make_id ( specie_label, skip_non_word_chars = True )
		rdf = f"""
			{exp_uri} schema:additionalProperty {specie_uri}.
			{specie_uri} a schema:PropertyValue;
				schema:propertyID "organism";
				schema:value "{specie_label}";
		"""
		rdf = dedent ( rdf )
		
		specie_terms = specie2terms.get ( specie_label )
		if specie_terms:
			rdf_terms = ", ".join ( [ "<" + s + ">" for s in specie_terms ] )
			rdf += "\tdc:type " + rdf_terms + ";\n"
		
		rdf += ".\n"
		return rdf

	def rdf_publication ( exp_uri, exp_js ):
		if "bibliography" not in exp_js: return ""
		rdf = ""
		for pub_js in exp_js [ "bibliography" ]:
			# Without this very minimum, it's hardly a meaningful entry
			if not ( "title" in pub_js or "accession" in pub_js or "doi" in pub_js ): continue
			if "accession" in pub_js:
				pub_uri = "bkr:pmid_" + str ( pub_js [ "accession" ] )
			elif "doi" in pub_js: pub_uri = pub_js [ "doi" ]
			else: pub_uri = "bkr:pub_" + hash_generator ( pub_js.values () )
			
			rdf += f"""
				{exp_uri} schema:subjectOf {pub_uri}.
				{pub_uri} a agri:ScholarlyPublication;
			"""
			rdf = dedent ( rdf )

			rdf += rdf_str ( pub_js, "title", "\tdc:title" )
			rdf += rdf_str ( pub_js, "authors", "\tagri:authorsList" )
			rdf += rdf_str ( pub_js, "accession", "\tagri:pmedId" )
			rdf += rdf_str ( pub_js, "doi", "\tagri:doiId" )
			rdf += rdf_str ( pub_js, "year", "\tschema:datePublished" )
			
			rdf += ".\n"

		return dedent ( rdf )


	exp_acc = exp_js [ "accession" ]
	exp_uri = make_ae_exp_uri ( exp_acc )
	
	rdf = f"""
		{exp_uri} a bioschema:Study;
			schema:identifier "{exp_acc}";
	"""
	rdf = dedent ( rdf )
	rdf += rdf_str ( exp_js, "name", "\tdc:title" )
	
	# TODO: not clear why they're arrays
	if exp_js [ "description" ]:
		rdf += rdf_str ( exp_js [ "description" ] [ 0 ], "text", "\tschema:description" )
	
	rdf += rdf_str ( exp_js, "releasedate", "\tschema:datePublished" )

	# gxaAnalysisType is added by gxa.gxa_get_experiment_descriptors() and they can be 'Differential', 'Baseline'
	# Detailed specifications for such types are in gxa-defaults.ttl, here we create a link to the corresponding 
	# URIs used there
	#
	rdf += rdf_pval (
		exp_js, "gxaAnalysisType", "\tschema:additionalProperty", 
		lambda gxa_type: "bkr:gxa_analysis_type_" + make_id ( gxa_type, skip_non_word_chars = True ) 
	)	
	
	rdf += ".\n"
	
	for specie in exp_js.get ( "organism", [] ):
		rdf += rdf_specie ( exp_uri, specie )
	rdf += rdf_publication ( exp_uri, exp_js )
	
	if out:
		print ( rdf, file = out )
	else:
		return rdf
# /end: rdf_ae_experiment

"""
	Builds a Knetminer URI for an ArrayExpress experiment.
"""
def make_ae_exp_uri ( exp_acc ) -> str:
	return "bkr:exp_" + exp_acc	 
