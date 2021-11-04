# Manages the arabidospis dataset
# TODO: we need to introduce dataset parameters, like the rres build pipeline 

# Use this prolog to go to the script's directory
cd "`dirname ${BASH_SOURCE[0]}`"

. ./rres-env.sh
export KNET_DATASET_DIR="$KNET_DATA_DIR/pub/endpoints/arabidopsis/51"
