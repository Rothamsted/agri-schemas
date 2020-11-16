# Use this prolog to go to the script's directory
mydir="$(pwd)"
cd "$(dirname ${BASH_SOURCE[0]})"

export DFW_ETL="$(pwd)"
export ETL_TOOLS="$DFW_ETL/etl-tools"

. "$ETL_TOOLS/brandizi-env.sh" # Defines some stuff like PYTHONPATH

export ETL_OUT="$DFW_ETL/output" # Overwrites the value set by the etl-tools script.
export NAMESPACES_PATH="$mydir/namespaces.ttl"
export JAVA_TOOL_OPTIONS="-Xmx8G"

for mod in etl-tools gxa
do
	. "$mydir/$mod/brandizi-env.sh"
	cd "$mydir"
done

conda activate snakemake # To be seen if needed in production too
