import logging
from sys import stdout
from textwrap import dedent

import math
from typing import Any
from urllib.error import HTTPError, URLError

from agrischemas.etltools.utils import rdf_str, rdf_text, make_id, hash_generator
from agrischemas.kpyutils import web


log = logging.getLogger ( __name__ )


"""
	Gets ArrayExpress experiments accessions, using the BioStudies API.
	
	As organisms, you can pass either a single string or a generator.

	A dictionary is returned such that the keys are experiment accessions and the values
	are dictionaries corresponding to the JSON objects that AE gives us.
	
	The link_type=gxa param is used, cause we are interested in GXA experiments only.

	Note about paging: BioStudies pages the result, so we recursively call the API with all 
	the pages and we return the merge of all page results. If you call the function without
	the page param, you'll get the merge from page 1. 
"""
def ae_get_experiment_accessions ( organisms, page = 1 ) -> dict:
	if type ( organisms ) == str: organisms = [ organisms ]
	if page == 1:
		log.info ( "Getting AE descriptors about %s", organisms )
	else:
		log.debug ( "Getting AE descriptors about %s, page %d", organisms, page )

	organism_search_str = " OR ".join ( [ 'organism:"' + o + '"' for o in organisms ] )

	url = "https://www.ebi.ac.uk/biostudies/api/v1/ArrayExpress/search?"
			
	# OR query needs to be done using Lucene syntax
	# (https://github.com/EBIBioStudies/biostudies-backend-services/issues/901)
	url += web.url_param ( "query", organism_search_str )

	url += web.url_param_append ( "link_type", "gxa" )
	url += web.url_param_append ( "pageSize", "100" ) # max allowed
	url += web.url_param_append ( "page", str ( page ) )

	aejs = web.url_get_json ( url )
	hits = aejs [ "hits" ]
	# Use a set to skip duplicated entries and for performace
	result = { hit [ "accession" ] for hit in hits if hit [ "isPublic" ] }

	total_hits = aejs [ "totalHits" ]
	page_size = aejs [ "pageSize" ]
	total_pages = math.ceil ( total_hits / page_size )
	if page == 1: log.debug ( "Total pages: %d, hits: %d, page size: %d", total_pages, total_hits, page_size )

	if page < total_pages:
		result.update ( ae_get_experiment_accessions ( organisms, page + 1 ) )
	
	return result
# /ens:ae_get_experiment_accessions()

"""
	Get JSON details for an ArrayExpress experiment, using the BioStudies API, after having
	done some additions and adjustments, such as adding our own 'aeTechnologyType' annotation.
	
	This is furher enriched later, by gxa_get_experiment_descriptors(), which adds GXA-specific
	details coming from the GXA API.
"""
def ae_get_experiment_descriptor ( exp_accession: str ):
	try:
		url = "https://www.ebi.ac.uk/biostudies/api/v1/studies/" + exp_accession
		result = web.url_get_json ( url )
	except Exception as ex:
		# Rethrow with the URL included
		raise URLError ( f"Error while getting AE experiment descriptor from {url}: {ex}" ) from ex

	# The AE Tech Type is a specific flag that must be used in GXA to build data download paths

	section = result.get ( "section", {} )
	attribs = section.get ( "attributes", [] )
	attribs = attribs2dict ( attribs )
	ae_tech = attribs.get ( "Study type", [] )
	if not type ( ae_tech ) is list: ae_tech = [ ae_tech ]

	ae_tech = \
		"Microarray" if "transcription profiling by array" in ae_tech \
		else ( 
			"RNASeq" if "RNA-seq of coding RNA" in ae_tech
			else None
		)

	# If it's not a technology we support here, skip by returning an empty result
	# TODO: we don't support "RNA-seq of coding RNA from single cells" yet
	if not ae_tech: return {}

	result [ "aeTechnologyType" ] = ae_tech

	return result


"""
	Renders the RDF about an ArrayExpress/GXA experiment, taking its description from the JSON returned
	by the BioStudies API, ie, ae_get_experiment_descriptors.
	
	out is passed to print ()'s file parameter, ie, it's the destination stream. If set to None explicitly,
	a string is generated and returned.	
"""
def rdf_ae_experiment ( exp_js: dict, out = stdout ) -> str:

	# TODO: Pull it out, it's useful elsewhere too
	specie2terms = { 
		"Arabidopsis thaliana": [ "http://purl.bioontology.org/ontology/NCBITAXON/3702" ],
		"Triticum aestivum": [ "http://purl.bioontology.org/ontology/NCBITAXON/4565" ]
	}

	def rdf_specie ( exp_uri:str, specie_label:str ):
		if not specie_label: return ""
		specie_uri = "bkr:specie_" + make_id ( specie_label, skip_non_word_chars = True )
		rdf = f"""
			{specie_uri} a agri:FieldTrialMaterialSource, schema:BioChemEntity;
				schema:name "{specie_label}";
				schema:subjectOf {exp_uri};
		"""
		rdf = dedent ( rdf )
		
		specie_terms = specie2terms.get ( specie_label )
		if specie_terms:
			rdf_terms = ", ".join ( [ "<" + s + ">" for s in specie_terms ] )
			rdf += "\tbioschema:taxonomicRange " + rdf_terms + ";\n"			
			rdf += "\tdc:type " + rdf_terms + ";\n"
		
		rdf += ".\n"
		return rdf
	# /end: rdf_specie ()

	def rdf_publication ( exp_uri, exp_js ):
		# Extract it from subsections
		section = exp_js.get ( "section", {} )
		subsections = section.get ( "subsections", [] )
		if not subsections: return ""

		pub_js = next ( 
			( js_obj for js_obj in subsections 
		  	if type (js_obj) is dict and js_obj [ "type" ] == "Publication" ),
			None
		)
		if not pub_js: return ""

		pub_attribs = attribs2dict ( pub_js.get ( "attributes", [] ) )

		pmed_id = pub_js.get ( "accno" )
		doi = pub_attribs.get ( "DOI" )
		title = pub_attribs.get ( "Title" )
		authors = pub_attribs.get ( "Authors" )

		# Without this very minimum, it's hardly a meaningful entry
		if not ( pmed_id or doi or title ): return ""

		rdf = ""

		if pmed_id: pub_uri = "bkr:pmid_" + pmed_id
		elif doi: pub_uri = doi
		else: pub_uri = "bkr:pub_" + hash_generator ( ( title, authors ) )
	
	  # We don't know if it's an article, 
		rdf += f"""
		{exp_uri} schema:subjectOf {pub_uri}.
		{pub_uri} a agri:ScholarlyPublication;
		"""
		rdf = dedent ( rdf )

		rdf += rdf_text ( pub_attribs, "Title", "\tdc:title" )
		rdf += rdf_text ( pub_attribs, "Authors", "\tagri:authorsList" )

		for (acc, acc_type, agri_acc_prop) in ( 
			(pmed_id, "PubMed ID", "pmedId"), 
			(doi, "DOI", "doiId" )
		):
			if not acc: continue
			rdf += f"""

				agri:{agri_acc_prop} "{acc}";
			 	schema:identifier [
					a schema:PropertyValue;
					schema:propertyID "{acc_type}";
					schema:value "{acc}";
				];
			"""

		# TODO: year seems to be missing from Biostudies
		rdf += rdf_str ( pub_attribs, "Year", "\tschema:datePublished" )
		
		rdf += ".\n"

		return rdf
	# /end: rdf_publication()

	# TODO: AE descriptors have entries about the design that should be reported here
	def rdf_exp_design ( exp_uri, exp_js ):
		ae_tech = exp_js [ "aeTechnologyType" ]
		# Match the default URI
		if not ae_tech == "Microarray": ae_tech = "rna_sequencing"
		ae_tech_uri = "bkr:ae_technology_type_" + make_id ( ae_tech )

		gxa_analysis = exp_js [ "gxaAnalysisType" ]
		gxa_analysis_uri = "bkr:gxa_analysis_type_" + make_id ( gxa_analysis )

		# TODO: onto terms
		tech_label = "Transcription profiling by array" if ae_tech == "Microarray" \
			else "RNA-seq of coding RNA"

		rdf = f"""
		{exp_uri} bioschema:studyProcess {exp_uri}_design.
		{exp_uri}_design a agri:ExperimentalDesign, schema:PropertyValue;
			schema:name "study design";
			schema:propertyID ppeo:experimental_design;
			dc:type <http://purl.obolibrary.org/obo/OBI_0500014>; # factorial design
			schema:description "Factorial design, technology: {tech_label}, analysis type: {gxa_analysis}.";

			schema:additionalProperty {ae_tech_uri}, {gxa_analysis_uri};
		.
		"""
		return dedent ( rdf )

	exp_acc = exp_js [ "accno" ]
	exp_uri = make_ae_exp_uri ( exp_acc )
	
	rdf = f"""
		{exp_uri} a bioschema:Study;
			schema:identifier "{exp_acc}";
	"""
	rdf = dedent ( rdf )

	top_attrs = attribs2dict ( exp_js [ "attributes" ] )
	section_attrs = attribs2dict ( exp_js [ "section" ] [ "attributes" ] )

	rdf += rdf_text ( top_attrs, "Title", "\tdc:title" )
	rdf += rdf_text ( section_attrs, "Description", "\tschema:description" )
	rdf += rdf_str ( top_attrs, "ReleaseDate", "\tschema:datePublished" )

	rdf += ".\n"
	
	# TODO: can we have multiple species? How is it represented?
	#
	species = section_attrs.get ( "Organism", None )
	if species:
		if type ( species ) == str: species = [ species ] 
		for specie in species:
			rdf += rdf_specie ( exp_uri, specie )

	rdf += rdf_exp_design ( exp_uri, exp_js )	
	rdf += rdf_publication ( exp_uri, exp_js )

	if out:
		print ( rdf, file = out )
	else:
		return rdf
# /end: rdf_ae_experiment


def attribs2dict ( 
	attribs: list[dict], key_name: str = 'name', value_name: str = 'value'
) -> dict[str, list[Any]]:
	"""
		Converts a list of attribute dictionaries (as returned by the BioStudies API) into
		a regular dictionary mapping attribute names to values.

		In other words, converts something like this:

		```javascript
		[ { 'name': 'Type', 'value': 'Type A' },
			{ 'name': 'Type', 'value': 'Type B' },
			{ 'name': 'Description', 'value': 'No library prep needed' } ]
		```

		into this:
		```javascript
		{ 'Type': [ 'Type A', 'Type B' ],
		  'Description': 'No library prep needed' }
		```

		As you can see, values can be either singletons or lists, depending on whether
		there are multiple values for the same key or not.

		TODO: onto terms
		TODO: tests
	""" 

	result = {}
	for attr in attribs:
		k, v = attr [ key_name ], attr [ value_name ]
		if k in result:
			old_v = result [ k ]
			if type ( old_v ) is list:
				if not v in old_v: old_v.append ( v )
			else:
				if v != old_v: result [ k ] = [ old_v, v ]
		else:
			result [ k ] = v
	return result



def _attribs2dict ( 
	attribs: list[dict], key_name: str = 'name', 
	value_name: str = 'value',
	has_multi_values: bool = True
) -> dict[str, list[Any]]:
	"""
		Converts a list of attribute dictionaries (as returned by the BioStudies API) into
		a regular dictionary mapping attribute names to values.

		In other words, converts something like this:

		```javascript
		[ { 'name': 'Type', 'value': 'Type A' },
			{ 'name': 'Type', 'value': 'Type B' },
			{ 'name': 'Description', 'value': 'No library prep needed' } ]
		```

		into this:
		```javascript
		{ 'Type': [ 'Type A', 'Type B' ],
		  'Description': [ 'No library prep needed' ] }
		```

		As you can see, values are always lists, to account for multiple values per key.

		If `has_multi_values` is False, assumes that there aren't multi-values attributes and 
		returns singletons. Raise an error if that's not the case.

		TODO: onto terms
		TODO: tests
	""" 

	result = {}
	for attr in attribs:
		k, v = attr [ key_name ], attr [ value_name ]
		if k in result:
			if has_multi_values:
				result [ k ].append ( v )
				continue
			if not v in result [ k ]:
				raise ValueError ( f"attribs2dict(): attribute '{k}' has multiple values "
					"but has_multi_values is False: " + ", ".join ( result [ k ] + [ v ] )
				)
		else:
			result [ k ] = [ v ] if has_multi_values else v 
	return result


"""
	Builds a Knetminer URI for an ArrayExpress experiment.
"""
def make_ae_exp_uri ( exp_acc ) -> str:
	return "bkr:exp_" + exp_acc	 
