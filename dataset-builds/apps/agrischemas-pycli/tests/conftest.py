import os
from brandizpyes.logging import logger_config

def pytest_configure ( config ):
	"""
	As per their docs, this is picked up by pytest at startup.
	"""

	cfg_path = os.path.dirname ( __file__ ) + "/resources/logging-test.yml"
	logger_config ( __name__, cfg_path )
