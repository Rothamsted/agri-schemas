# Parse the CLI options
# 
_filtered_args=()
while [[ $# -gt 0 ]]
do
	opt_name="$1"
  case $opt_name in
  	# WARNING: these '--:' special markers are used by --help to generate explanations about the available
  	# options.
  	#--: The environement ID. This triggers the initialisation from a file like 'environments/<env-id>-env.sh'.
  	--env)
  		export KETL_ENV_ID="$2"; shift 2;;
  	#--: yields this help output and then exits with 1
  	--help|-h)
  		echo -e "\n"
  		# Report the options
  		cat <<EOT
==== The AgriSchemas Data build ETL ===

=== Options:
	
EOT

			egrep -i '(#\-\-:|\-\-[a-z,0-9,-,_].+\))' "$0" | sed s/'^\s*#\-\-:/#/g' | sed -E s/'^\s+(\-\-.+)\)'/'\1\n'/g

			cat <<EOT

All the other options are passed to the following command,eg, the Snakemake command 
that launches the ETL workflow.
			
EOT

  		exit 2;;
  	*)
  		_filtered_args+=("$1")
			shift;;
	esac
done

# Pass the leftovers down
set -- "${_filtered_args[@]}"

if [[ -z "$KETL_ENV_ID" ]]; then
	printf "\n\n  --env is missing, try -h\n\n"
	exit 2
fi

# Defaults
#
cd "$(dirname "${BASH_SOURCE[0]}")"

export ETL_HOME="$(realpath .)"
export ETL_OUT="$ETL_HOME/output"
export ETL_TMP="$ETL_OUT/tmp"

# Not used to build the data or upload them, only for admin scripts about the Virtuoso server
export ETL_VIRTUOSO_DATA_DIR="$ETL_TMP/virtuoso-data"

# Specific env
# 
cd "$ETL_HOME"
printf "\n\n  Sourcing environment '%s'...\n" "$KETL_ENV_ID"
. ./"environments/${KETL_ENV_ID}-env.sh"

# In case they cd-ed somewhere else
cd "$ETL_HOME"

printf '  ...Done, ETL_HOME="%s"\n\n' "$ETL_HOME"