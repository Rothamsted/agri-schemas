# These are needed for tests

cd "`dirname ${BASH_SOURCE[0]}`"
export KNET_ETL_DIR="`pwd`"
cd ..
. config/environments/rres-env.sh

export ETL_SNAKE_OPTS="--profile $DFW_ETL/config/snakemake/rres-slurm-knet"

cd "$KNET_ETL_DIR"
