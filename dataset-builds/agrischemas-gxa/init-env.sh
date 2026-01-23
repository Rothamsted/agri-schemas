export KETL_ENV_ID="$1"

if [[ -z "$KETL_ENV_ID" ]]; then
	printf "\n\n  Usage: "$(basename "$0")" <env-id>\n\n"
	exit 2
fi

# Defaults
#
cd "$(dirname "${BASH_SOURCE[0]}")"
mydir="$(pwd)"
cd ..

export ETL_HOME="$(realpath .)"
export ETL_OUT="$ETL_HOME/output"
export ETL_TMP="$ETL_OUT/tmp"

cd "$mydir"
printf "\n\n  Sourcing environment '%s'...\n" "$KETL_ENV_ID"
. ./"environments/${KETL_ENV_ID}-env.sh"

# In case they cd-ed somewhere else
cd "$mydir"

printf '  ...Done, ETL_HOME="%s"\n\n' "$ETL_HOME"
