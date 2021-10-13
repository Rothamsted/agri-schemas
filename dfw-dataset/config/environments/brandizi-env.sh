# Use this prolog to go to the script's directory
cd "`dirname ${BASH_SOURCE[0]}`"

cd ../..
export DFW_ETL="`pwd`"

cd ..
export AG_DIR="`pwd`"

export ETL_OUT="$DFW_ETL/output" # Overwrites the value set by the etl-tools script.
export ETL_TMP="$ETL_OUT/tmp" # temp stuff produced by the pipeline

export JENA_HOME=/Applications/local/dev/semantic_web/jena

# These are personal! Please, do not use elsewhere!
export BIOPORTAL_APIKEY='a9f8528b-4db9-4f35-995f-14e81106615f'
export AGROPORTAL_APIKEY='c5a0f99c-a061-4175-8d7e-e49c47b6337d'

export NAMESPACES_PATH="$DFW_ETL/namespaces.ttl"
export JAVA_TOOL_OPTIONS="-Xmx8G"
export ETL_LOG_CONF="$AG_DIR/lib/etltools/logging-test.yaml" # or logging.yaml for production

#for mod in lib dfw-dataset/knetminer dfw-dataset/gxa
#do
#	for prefix in default brandizi
#	do
#		script="$AG_DIR/$mod/$prefix-env.sh"
#		[[ -e "$script" ]] && . "$script"
#		cd "$AG_DIR"
#	done
#done

. ~/bin/conda-init.sh
conda activate snakemake

cd "$DFW_ETL"
