#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

. ./init-env.sh # Our envs and Python venvs are two different things

# Idempotent, installs what's needed or does nothing
. ./update.sh

mkdir -p "$ETL_TMP" # needed by the logger

# if --cores all isn't already in the CLI arguments, add it
if [[ ! " $* " =~ " --cores all " ]]; then
	set -- "$@" --cores all
fi

snakemake --snakefile data-build.snakefile "$@"