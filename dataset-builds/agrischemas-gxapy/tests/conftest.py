import os

from brandizpyes.logging import logger_config

"""
Pytest configuration file, which the framework picks up at startup.

[Details here](https://docs.pytest.org/en/stable/reference/fixtures.html)

"""
def pytest_configure ( config ):
	"""
	As per their docs, this is picked up by pytest at startup.
	"""

	cfg_path = os.path.dirname ( __file__ ) + "/resources/logging-test.yml"
	logger_config ( __name__, cfg_path )

	# This is what their UI uses, but probably they don't like that others reuse them,
	# so, don't do it in regular code.
	os.environ [ 'BIOPORTAL_APIKEY' ] = "8b5b7825-538d-40e0-9e9e-5ab9274a9aeb"
	os.environ [ 'AGROPORTAL_APIKEY' ] = "1de0a270-29c5-4dda-b043-7c3580628cd5"


