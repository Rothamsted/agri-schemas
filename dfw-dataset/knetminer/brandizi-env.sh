# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
export KNET_ETL_DIR="`pwd`"
cd ..
. config/environments/brandizi-env.sh

# Used for testing
export OXL2NEO_HOME="$HOME/Documents/Work/RRes/ondex_git/ondex-knet-builder/ondex-knet-builder/modules/neo4j-export/target/neo4j-exporter"
export KNET_RDF_DIR="/tmp/knet-poaceae-rdf"

cd "$KNET_ETL_DIR"
