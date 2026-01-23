import os, logging
from agrischemas.etltools.utils import get_commented_traceback
from agrischemas.ebigxa.gxa import gxa_rdf_all_save, gxa_get_analysis_types_cached, annotate_condition
from brandizpyes.logging import logger_config
import pathlib
import json
import bz2
import time

log = logger_config ( __name__, use_unsafe_loader = True )

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

GXA_ANALYSIS_TYPES = gxa_get_analysis_types_cached ( GXA_ORGANISMS, ETL_TMP + "/gxa-analysis-types.json" )
if not EXPERIMENT_ACCS: EXPERIMENT_ACCS = GXA_ANALYSIS_TYPES.keys ()
OUT_PATTERN = ETL_OUT + "/gxa/{exp_acc}.ttl.bz2" 


#### The meat
#

rule all:
	message:
		"Exporting All"
	input:
		expand ( OUT_PATTERN, exp_acc = EXPERIMENT_ACCS )
	

rule single_exp:
	message:
		"{wildcards.exp_acc} RDF Dump"
	output:
		OUT_PATTERN
	run:
		log = logging.getLogger ( __name__ )
		fout = output [ 0 ]
		try:
			gxa_rdf_all_save ( wildcards.exp_acc, GXA_ANALYSIS_TYPES [ wildcards.exp_acc ], fout, compress = True )
		except Exception as ex:
			log.error ( 
				"Error while exporting %s: %s. Ignoring this accession, details in the log file", 
				wildcards.exp_acc,
				str ( ex )
			)
			log.debug ( "Details: %s", ex, exc_info = True )
			with bz2.open ( fout, "w" ) as bout:
				bout.write ( ( "# Export error: %s\n\n" % str ( ex ) ).encode () )
				bout.write ( get_commented_traceback ( "# " ).encode () )

