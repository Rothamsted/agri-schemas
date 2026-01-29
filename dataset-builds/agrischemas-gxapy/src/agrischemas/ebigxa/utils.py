from posixpath import dirname
from textwrap import dedent
from agrischemas.etltools.utils import XNamespaceManager


def rdf_gxa_namespaces () -> str:
	"""
		The GXA-relevant namespaces.

		These are read from the `gxa-rdf-defaults.ttl` file using :class:`XNamespaceManager`
	"""

	ns_mgr = XNamespaceManager ()
	ns_mgr.load ( dirname ( __file__ ) + "/gxa-rdf-defaults.ttl" )

	return ns_mgr.to_turtle () + "\n"
