# Use this prolog to go to the script's directory
mydir="$(pwd)"
cd "$(dirname ${BASH_SOURCE[0]})"

export DFW_ETL="$(pwd)"
export ETL_TOOLS="$DFW_ETL/etl-tools"

. "$ETL_TOOLS/brandizi-env.sh" # Defines some stuff like PYTHONPATH

export ETL_OUT="$DFW_ETL/output" # Overwrites the value set by the etl-tools script.

export NAMESPACES_PATH="$mydir/namespaces.ttl"

# These are needed for tests
export ODX2RDF="$HOME/Documents/Work/RRes/ondex_git/ondex-knet-builder/ondex-knet-builder/modules/rdf-export-2-cli/target/rdf-export-2-cli_4.0-SNAPSHOT"

export KNET_RDF_DIR="/tmp/knet-wheat-rdf"
export JAVA_TOOL_OPTIONS="-Xmx8G"

# Since you're sourcing me (". $0"), you typically want to go back to the initial workdir
cd "$mydir"

conda activate snakemake # To be seen if needed in production too
