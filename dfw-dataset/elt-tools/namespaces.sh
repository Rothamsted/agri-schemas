if [[ -z ${NAMESPACES+x} ]]; then
	NAMESPACES="@prefix ex: <http://www.example.com/ns/>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix owl: <http://www.w3.org/2002/07/owl#>.
@prefix schema: <http://schema.org/>.
"
	export NAMESPACES
fi

function sparql_ns
{
	nss="${1:-$NAMESPACES}"
	echo "$nss" | sed -E -e s/'@prefix'/'PREFIX'/gi -e s/'\.(\s*)$'/'\1'/g -e s/'\.(\s*\@prefix)'/'\1'/g
}
export -f sparql_ns

function ns {
  prefix="$1"
	nss="${2:-$NAMESPACES}"
	echo "$nss" | sed -E "s/\s*@prefix\s+$prefix:\s<([^<>]+)>\s*\.*/\1/gi;t;d"
}
export -f ns
