#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

# TODO: Poor! We need --env-id and argument parsing that retains our own args and 
# sends all the rest to Snakemake.
. ./init-env.sh "$@" # Our envs and Python venvs are two different things

# Idempotent, installs what's needed or does nothing
. ./install.sh

mkdir -p "$ETL_TMP" # needed by the logger

snakemake --snakefile data-build.snakefile --cores all
