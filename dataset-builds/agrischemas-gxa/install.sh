#!/usr/bin/env bash
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ ! -d .venv ]]; then
	printf "\n  Creating virtual environment in %s/.venv\n" "`pwd`"
	python3 -m venv .venv
fi

printf "\n  Activating the Python environment\n"
. .venv/bin/activate

printf "\n  Installing/upgrading Python dependencies\n"
# TODO: --force is only for local packages and during development, let's use another requirements
# list
pip install --upgrade --force -r requirements.txt

printf "\n  Installation/upgrade done.\n"
