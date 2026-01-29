# Defaults
#
cd "$(dirname "${BASH_SOURCE[0]}")"
myname="$(basename "$(pwd)")"
cd ..

. ./"init-env.sh"

# Defaults, if any, go here
#

# Then, we source our own env
#
cd "$ETL_HOME/$myname"
printf "\n\n  Sourcing environment '%s' for agrischemas-gxa...\n" "$KETL_ENV_ID"
. ./"environments/${KETL_ENV_ID}-env.sh"

# In case they cd-ed somewhere else
cd "$ETL_HOME/$myname"

printf '  ...Done, ETL_HOME="%s"\n\n' "$ETL_HOME"
