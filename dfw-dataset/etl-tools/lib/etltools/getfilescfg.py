import os
from snakemake.io import expand
from etltools.utils import check_env

INPUTS = ""
TARGET_DIR = ""
OUT_FILES = ""

def init_config ( config ):
	check_env ()
	global INPUTS, TARGET_DIR, OUT_FILES
	INPUTS = config [ "static_files" ]
	TARGET_DIR = os.getenv ( "ETL_OUT" ) + "/" + config [ "target_dir" ]
	OUT_FILES = expand ( TARGET_DIR + "/{out}", out = INPUTS.keys () )
