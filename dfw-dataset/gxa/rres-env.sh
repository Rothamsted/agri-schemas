# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
. default-env.sh
cd ..
. config/environments/rres-env.sh

export AG_DATA_DIR="$KNET_DATA_DIR/pub/endpoints/agri-schemas"
export ETL_OUT="$AG_DATA_DIR/gxa/v202110"
export ETL_TMP="$AG_DATA_DIR/tmp"

cd "$GXA_ETL_DIR"
