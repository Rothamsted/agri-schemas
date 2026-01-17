"""
  Simple implementation of clients to invoke Bioportal APIs
"""
from agrischemas.kpyutils import web
import os

import logging
log = logging.getLogger ( __name__ )

"""
	The BioPortal client.

	Instances must be inititalised with an API key, which is then reused as necessary.
"""
class BioPortalClient:
	
	BIO_PORTAL_BASE_URL = "http://data.bioontology.org"
	
	"""
	  if apikey is missing, tries from os.env ( BIOPORTAL_APIKEY )
	"""
	def __init__ ( self, apikey = None):
		self._my_init ( apikey, "BIOPORTAL_APIKEY", BioPortalClient.BIO_PORTAL_BASE_URL )

	def _my_init ( self, apikey, apikey_env_var, base_url ):
		if not apikey: apikey = os.getenv ( apikey_env_var )
		if not apikey: raise TypeError ( 
			f"{self.__class__.__name__} needs an APIKEY, either on the constructor, or from " + 
			f"the {apikey_env_var} OS variable. Register to their site to get a key."
		)
		self.apikey = apikey
		self._base_url = base_url
		
		
		

	"""The API base URL, including the apikey"""
	def _bp_baseurl ( self, api_path ):
		return self._base_url + api_path + "?" + web.url_param ( "apikey", self.apikey )

	"""
		The text annotation service

		This returns the plain json.
	"""
	def annotator ( self, text, **other_params ):
		other_params [ "text" ] = text
		url = self._bp_baseurl ( "/annotator" )
		url = web.url_build ( url, **other_params )
		jterms = web.url_get_json ( url )
		return jterms

	"""
		The text annotation service

		Returns the a list term descriptors, which are also cutoff based on the corresponding parameter.
		The annotar should return terms in order of significance, so the cutoff should retain the most relevant ones.

		:param cutoff: cuts the list of returned terms, filtering the top-ranked only
		:param only_uris: if set, returns only the term URIs (instead of complete dictionaries with label, synonym, definition).
	"""
	def annotator_terms ( self, text, cutoff = None, only_uris = False, **other_params ):
		jterms = self.annotator ( text, **other_params )
		# Strangely, there are dupes, let's filter
		visited = set (); new_terms = []
		for term in jterms:
			uri = term [ "annotatedClass" ] [ "@id" ]
			if uri in visited: continue
			new_term = { "uri": uri }
			new_term [ "self" ] = term [ "annotatedClass" ] [ "links" ] [ "self" ]
			new_terms.append ( new_term )
			visited.add ( uri )
		if cutoff and len ( new_terms ) > cutoff:
			new_terms = new_terms [ 0: cutoff ]
		if only_uris:
			new_terms = [ term [ "uri" ] for term in new_terms ]
			return new_terms
		# Else, let's resolve only those that were retained
		for new_term in new_terms:
			durl = new_term [ "self" ]
			durl += "?" + web.url_param ( "apikey", self.apikey )
			dj = web.url_get_json ( durl )
			new_term [ "label" ] = dj [ "prefLabel" ]
			new_term [ "synonyms" ] = dj [ "synonym" ]
			defv = dj [ "definition" ]
			defv = defv [ 0 ] if len ( defv ) > 0 else "" # TODO: why is it string?
			new_term [ "definition" ] = defv
		return new_terms
		
class AgroPortalClient ( BioPortalClient ):
	AGRO_PORTAL_BASE_URL = "http://services.agroportal.lirmm.fr"
	
	def __init__ ( self, apikey = None ):
		self._my_init ( apikey, "AGROPORTAL_APIKEY", AgroPortalClient.AGRO_PORTAL_BASE_URL )
