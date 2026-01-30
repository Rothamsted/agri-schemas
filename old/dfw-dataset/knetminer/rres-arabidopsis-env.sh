# Manages the arabidospis dataset
# TODO: we need to introduce dataset parameters, like the rres build pipeline 

cd "`dirname ${BASH_SOURCE[0]}`"

export KNET_DATA_DIR=/home/data/knetminer
export KNET_DATASET_DIR="$KNET_DATA_DIR/pub/endpoints/arabidopsis/51"
. ./rres-env.sh
