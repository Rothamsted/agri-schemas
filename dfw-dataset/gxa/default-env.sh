cd "$(dirname ${BASH_SOURCE[0]})"
export GXA_ETL_DIR="`pwd`"

for entry in "$GXA_ETL_DIR/lib"
do
	[[ "$PYTHONPATH" =~ "$entry" ]] && continue 
  [[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
	PYTHONPATH="$PYTHONPATH$entry"
done
export PYTHONPATH

cd "$GXA_ETL_DIR"
