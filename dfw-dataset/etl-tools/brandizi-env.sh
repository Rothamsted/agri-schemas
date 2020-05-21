mydir="`pwd`"
cd "$(dirname ${BASH_SOURCE[0]})"
export ETL_TOOLS="`pwd`"

export JENA_HOME=/Applications/local/dev/semantic_web/jena
export ETL_OUT=/tmp/etl-tools

for entry in "$ETL_TOOLS/lib" /usr/local/lib/python3.7/site-packages
do
  [[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
  [[ "$PYTHONPATH" =~ "$entry" ]] || PYTHONPATH="$PYTHONPATH$entry"
done
export PYTHONPATH
