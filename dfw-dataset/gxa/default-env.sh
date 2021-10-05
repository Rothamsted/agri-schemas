cd "$(dirname ${BASH_SOURCE[0]})"
gxadir="`pwd`"

for entry in "$gxadir/lib"
do
	[[ "$PYTHONPATH" =~ "$entry" ]] && continue 
  [[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
	PYTHONPATH="$PYTHONPATH$entry"
done
export PYTHONPATH
