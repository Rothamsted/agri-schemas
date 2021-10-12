set -e

if [[ -z "$DFW_ETL" ]]; then 
	echo -e "\n\tNo DFW_ETL, source some \*env.sh file before me\n"
	exit 1
fi

cd "$DFW_ETL/knetminer"

echo -e "\n\tRunning the SnakeMake pipeline\n"
[[ -z "$KNET_SNAKE_OPTS" ]] && KNET_SNAKE_OPTS='--cores'
snakemake --snakefile data-build.snakefile $KNET_SNAKE_OPTS
