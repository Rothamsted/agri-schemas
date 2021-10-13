set -e

if [[ -z "$DFW_ETL" ]]; then 
	echo -e "\n\tNo DFW_ETL, source some \*env.sh file before me\n"
	exit 1
fi

cd "$DFW_ETL/gxa"

echo -e "\n\tRunning the SnakeMake pipeline\n"

snake_opts="$ETL_SNAKE_OPTS"
[[ -z "$snake_opts" ]] && snake_opts='--cores'
snakemake --configfile snake-config.yaml --snakefile data-build.snakefile $snake_opts
