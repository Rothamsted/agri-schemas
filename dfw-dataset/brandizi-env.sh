# Use this prolog to go to the script's directory
mydir="`pwd`"
cd "`dirname ${BASH_SOURCE[0]}`"

export DFW_ETL="`pwd`"

export ETL_OUT="$DFW_ETL/output" # Overwrites the value set by the etl-tools script.
export ETL_TMP="$ETL_OUT/tmp" # temp stuff produced by the pipeline

export JENA_HOME=/Applications/local/dev/semantic_web/jena

# These are personal! Please, do not use elsewhere!
export BIOPORTAL_APIKEY='a9f8528b-4db9-4f35-995f-14e81106615f'
export AGROPORTAL_APIKEY='c5a0f99c-a061-4175-8d7e-e49c47b6337d'

export NAMESPACES_PATH="$mydir/namespaces.ttl"
export JAVA_TOOL_OPTIONS="-Xmx8G"

cd ..
. lib/default-env.sh

for mod in gxa
do
	. "$mydir/$mod/brandizi-env.sh"
	cd "$mydir"
done

~/bin/conda-init.sh
conda activate snakemake

cd "$mydir"
