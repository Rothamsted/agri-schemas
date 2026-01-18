import os, logging
from etltools.utils import logger_config, get_commented_traceback
from ebigxa.gxa import gxa_rdf_all_save, gxa_get_experiment_descriptors_cached, annotate_condition
import pathlib
import json
import bz2
import time

log = logger_config ( __name__ )

## Get stuff from the environment

ETL_OUT = os.getenv ( "ETL_OUT" )
ETL_TMP = os.getenv ( "ETL_TMP" )


#### Config
#

# Test sample. If this is unset, all the accessions about the configured organisms 
# below will be exported.

EXPERIMENT_ACCS = [ 
	'E-MTAB-7521', 'E-MTAB-8326', 'E-MTAB-5137', 'E-MTAB-5132', 'E-MTAB-8073', 'E-MTAB-7050', 'E-MTAB-3287',
	'E-MTAB-6965', 'E-MTAB-7374', 'E-MTAB-6866'
]

GXA_ORGANISMS = [ "arabidopsis thaliana", "triticum aestivum" ]

# Sometimes, this is unstable, this option allows for switching to "BioPortal".
# They mainly differ for the list of supported ontologies.
annotate_condition.default_annotator = "AgroPortal"


#### Further globals. Hopefully, you won't need to change things below here
#

EXPERIMENTS_JS = gxa_get_experiment_descriptors_cached ( GXA_ORGANISMS, ETL_TMP + "/exp-descriptors.json" )
if not EXPERIMENT_ACCS: EXPERIMENT_ACCS = EXPERIMENTS_JS.keys ()
OUT_PATTERN = ETL_OUT + "/gxa/{exp_acc}.ttl.bz2" 


#### The meat
#

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

