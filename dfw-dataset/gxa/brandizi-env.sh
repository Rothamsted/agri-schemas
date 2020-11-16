cd "$(dirname ${BASH_SOURCE[0]})"
gxadir="`pwd`"

for entry in "$gxadir/lib" /usr/local/lib/python3.8/site-packages
do
	[[ "$PYTHONPATH" =~ "$entry" ]] && continue 
  [[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
	PYTHONPATH="$PYTHONPATH$entry"
done
export PYTHONPATH
