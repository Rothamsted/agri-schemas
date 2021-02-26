kpyutils_path="$(cd `dirname "${BASH_SOURCE[0]}"`/..; pwd)"

[[ -z "$PYTHONPATH" ]] || PYTHONPATH="$PYTHONPATH:"
PYTHONPATH="$PYTHONPATH$kpyutils_path"
export PYTHONPATH
