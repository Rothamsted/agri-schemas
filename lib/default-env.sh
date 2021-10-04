cd "`dirname ${BASH_SOURCE[0]}`"
export AG_LIB="`pwd`" # The Agrischema software library

if [[ ! "$PYTHONPATH" =~ "$AG_LIB" ]]; then
	[[ ! -z "$PYTHONPATH" ]] && PYTHONPATH="$PYTHONPATH:"
	export PYTHONPATH="$PYTHONPATH$AG_LIB"
fi

. etltools/default-env.sh
cd "$AG_LIB"