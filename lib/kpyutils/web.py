'''
	kpyutils - The Knetminer Python Utils

  Utilities about web, HTTP, web APIs and the like.

	:author: Marco Brandizi
'''

from urllib.parse import quote
from urllib.request import urlopen
import json

import logging
log = logging.getLogger ( __name__ )


"""
  Builds a URL parameter, including the URL-encoding of its value.
"""
def url_param ( key, value ):
	return key + "=" + quote ( value )

"""
  The same as url_param, but prepend a '&' separator.
"""
def url_param_append ( key, value ):
	return "&" + url_param ( key, value )

"""
  Builds a URL from a dictionary of parameters.
"""
def url_build ( baseurl, **params ):
	url = baseurl
	for key in params:
		url += url_param_append ( key, params [ key ] )
	return url

"""
	Simple helper to get the URL content
"""
def url_get_json ( url ):
	log.debug ( "url_get_json: <%s>", url )
	jdoc = urlopen ( url ).read()
	jdoc = json.loads( jdoc )
	return jdoc
