#!/bin/env bash
set -e

cd "`dirname ${BASH_SOURCE[0]}`"
. ./init-env.sh "$@"

if [[ -z "$$VIRTUAL_ENV" ]]; then
	# no .venv/, no party
	if [[ ! -d .venv || ! -f .venv/bin/activate ]]; then
		printf "\n\n  ERROR: No virtualenv found in %s/.venv, run install.sh\n\n" "`pwd`" 1>&2
		exit 2
	fi
	. .venv/bin/activate
fi

# TODO: continue with install.sh
# TODO: snake
