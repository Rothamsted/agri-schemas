import os, glob
from ebigxa.ae import rnaseqer_experiments_download_all
from etltools.utils import logger_config

log = logger_config ( __name__ )


ETL_OUT = os.getenv ( "ETL_OUT" )

rule all_gxa:
	output:
		glob.glob ( ETL_OUT + "/rdf/gxa-experiments.ttl" )
	message:
		"Aggregating all the files"
	
rule gxa_get_exp_rdf:
  input:
  	ETL_OUT + "/tmp/gxa/exp-accs.tsv"
  output:
  	ETL_OUT + "/rdf/gxa-experiments.ttl"
  message:
  	"Getting RDF for GXA Experiment descriptions"
  run:
	 	with open ( output [ 0 ], "w" ) as out:
	 		rdf_ae_experiments ( input [ 0 ], out )

rule gxa_get_exp_list:
  output:
  	ETL_OUT + "/tmp/gxa/exp-accs.tsv"
  message:
  	"Getting list of GXA experiments"
  run:
	 	with open ( output [ 0 ], "w" ) as out:
	 		rnaseqer_experiments_download_all ( config [ 'gxa_organisms' ], out )
