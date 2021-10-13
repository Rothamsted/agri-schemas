# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
. default-env.sh

cd ..
. config/environments/brandizi-env.sh

export ETL_OUT="$ETL_OUT/gxa"

cd "$GXA_ETL_DIR"
