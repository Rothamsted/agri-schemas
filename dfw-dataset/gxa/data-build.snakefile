import os, logging
from etltools.utils import logger_config, get_commented_traceback
from ebigxa.gxa import gxa_rdf_all_save, gxa_get_experiment_descriptors_cached, annotate_condition
import pathlib
import json
import bz2

log = logger_config ( __name__ )

ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TMP = os.getenv ( "ETL_TMP" )


EXPERIMENTS_JS = gxa_get_experiment_descriptors_cached ( config [ 'gxa_organisms' ], ETL_TMP + "/gxa/exp-descriptors.js" )
EXPERIMENT_ACCS = EXPERIMENTS_JS.keys ()

# Test sample
#EXPERIMENT_ACCS = [ 
#	'E-MTAB-7521', 'E-MTAB-8326', 'E-MTAB-5137', 'E-MTAB-5132', 'E-MTAB-8073', 'E-MTAB-7050', 'E-MTAB-3287',
#	'E-MTAB-6965', 'E-MTAB-7374', 'E-MTAB-6866'
#]

OUT_PATTERN = ETL_OUT + "/gxa/{exp_acc}.ttl.bz2" 

annotate_condition.default_annotator = config.get ( "text_annotator", annotate_condition.default_annotator )


rule all:
	message:
		"Exporting everything"
	input:
		expand ( OUT_PATTERN, exp_acc = EXPERIMENT_ACCS )
	

rule single_exp:
	message:
		"Getting RDF for {wildcards.exp_acc}"
	output:
		OUT_PATTERN
	run:
		log = logging.getLogger ( __name__ )
		fout = output [ 0 ]
		try:
			gxa_rdf_all_save ( EXPERIMENTS_JS [ wildcards.exp_acc ], fout, compress = True )
		except Exception as ex:
			log.error ( "Error while exporting %s, ignoring this accession %s", wildcards.exp_acc, str ( ex ) )
			log.debug ( "Details: %s", ex )
			with bz2.open ( fout, "w" ) as bout:
				bout.write ( ( "# Export error: %s\n\n" % str ( ex ) ).encode () )
				bout.write ( get_commented_traceback ( "# " ).encode () )
