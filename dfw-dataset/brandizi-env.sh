# Use this prolog to go to the script's directory
mydir="$(pwd)"
cd "$(dirname ${BASH_SOURCE[0]})"

export DFW_ETL="$(pwd)"
export ETL_TOOLS="$DFW_ETL/etl-tools"

. "$DFW_ETL/../biotools/default-env.sh"
# These are personal! Please, do not use elsewhere!
export BIOPORTAL_APIKEY='a9f8528b-4db9-4f35-995f-14e81106615f'
export AGROPORTAL_APIKEY='c5a0f99c-a061-4175-8d7e-e49c47b6337d'


. "$ETL_TOOLS/brandizi-env.sh" # Defines some stuff like PYTHONPATH

export ETL_OUT="$DFW_ETL/output" # Overwrites the value set by the etl-tools script.
export ETL_TMP="$ETL_OUT/tmp" # temp stuff produced by the pipeline

export NAMESPACES_PATH="$mydir/namespaces.ttl"
export JAVA_TOOL_OPTIONS="-Xmx8G"

for mod in etl-tools gxa
do
	. "$mydir/$mod/brandizi-env.sh"
	cd "$mydir"
done

. ../biotools/default-env.sh
cd "$mydir"

conda activate snakemake # To be seen if needed in production too
