import utils
import os
from snakemake.io import expand

INPUTS = ""
TARGET_DIR = ""
OUT_FILES = ""

def init_config ( config ):
	global INPUTS, TARGET_DIR, OUT_FILES
	INPUTS = config [ "static_files" ]
	TARGET_DIR = os.getenv ( "ELT_OUT" ) + "/" + config [ "target_dir" ]
	OUT_FILES = expand ( TARGET_DIR + "/{out}", out = INPUTS.keys () )

