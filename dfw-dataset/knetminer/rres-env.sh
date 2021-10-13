# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
export KNET_ETL_DIR="`pwd`"
cd ..
. config/environments/rres-env.sh

cd "$KNET_ETL_DIR"
