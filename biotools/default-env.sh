biotools_path="$(cd `dirname "${BASH_SOURCE[0]}"`/..; pwd)"

[[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
PYTHONPATH="$PYTHONPATH$biotools_path"
export PYTHONPATH
