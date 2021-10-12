set -e

if [[ -z "$DFW_ETL" ]]; then 
	echo -e "\n\tNo DFW_ETL, source some \*env.sh file before me\n"
	exit 1
fi

cd "$DFW_ETL/gxa"

echo -e "\n\tRunning the SnakeMake pipeline\n"
snakemake --cores --configfile snake-config.yaml --snakefile data-build.snakefile $GXA_SNAKE_OPTS
