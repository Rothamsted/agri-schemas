# Use this prolog to go to the script's directory
cd "`dirname ${BASH_SOURCE[0]}`"

export DFW_ETL="`pwd`"
cd ..
export AG_DIR="`pwd`"

export KNET_DATA_DIR=/home/data/knetminer
export KNET_DATASET_DIR="$KNET_DATA_DIR/pub/endpoints/poaceae/51"
export ETL_OUT="$KNET_DATASET_DIR/rdf" 
export ETL_TMP="$KNET_DATASET_DIR/tmp" # temp stuff produced by the pipeline

export JENA_HOME=/home/data/knetminer/software/jena

export KNET_SNAKE_OPTS="--profile config/snakemake/slurm"


# These are personal! Please, do not use elsewhere!
export BIOPORTAL_APIKEY='a9f8528b-4db9-4f35-995f-14e81106615f'
export AGROPORTAL_APIKEY='c5a0f99c-a061-4175-8d7e-e49c47b6337d'

export NAMESPACES_PATH="$DFW_ETL/namespaces.ttl"
export JAVA_TOOL_OPTIONS="-Xmx64G"
export ETL_LOG_CONF="$AG_DIR/lib/etltools/logging-test.yaml" # or logging.yaml for production

for mod in lib dfw-dataset/knetminer dfw-dataset/gxa
do
	for prefix in default rres
	do
		script="$AG_DIR/$mod/$prefix-env.sh"
		[[ -e "$script" ]] && . "$script"
		cd "$AG_DIR"
	done
done

conda activate snakemake

cd "$DFW_ETL"
