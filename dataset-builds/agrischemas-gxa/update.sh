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
pip install --upgrade -r requirements.txt
# Without --force, it won't see wheel rebuilds, with --force on all deps, 
# a lot of unnecessary deps are upgraded every time. 
# So, this separation is a way to deal wit it.
# Note that I'm not using --editable, cause it's too messy when there are transitive deps.
pip install --upgrade --force -r requirements-local.txt

printf "\n  Installation/upgrade done.\n"
