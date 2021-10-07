set -e

if [[ -z "$DFW_ETL" ]]; then 
	echo -e "\n\tNo DFW_ETL, source some \*env.sh file before me\n"
	exit 1
fi

cd "$DFW_ETL/knetminer"

echo -e "\n\tRunning the SnakeMake pipeline\n"
snakemake --cores --snakefile data-build.snakefile $KNET_SNAKE_OPTS
