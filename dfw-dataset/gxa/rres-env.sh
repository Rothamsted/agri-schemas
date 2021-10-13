# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
. default-env.sh
cd ..
. config/environments/rres-env.sh

export KNET_DATASET_DIR="$KNET_DATA_DIR/pub/endpoints/agri-schemas/gxa/v202110"
export ETL_OUT="$KNET_DATASET_DIR" 
export ETL_TMP="$KNET_DATASET_DIR/tmp"

cd "$GXA_ETL_DIR"
