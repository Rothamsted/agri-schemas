# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
. default-env.sh
cd ..
. config/environments/brandizi-env.sh

cd "$GXA_ETL_DIR"
