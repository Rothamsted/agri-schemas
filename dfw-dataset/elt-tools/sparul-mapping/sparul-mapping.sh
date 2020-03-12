work_dir="$(pwd)"
cd "$(dirname $0)"
my_dir="$(pwd)"
my_lib="$my_dir/lib"
cd "$work_dir"

tdb_file="$1"
export TARGET_NS="$2"
export TARGET_GRAPH="$3"
dump_file="$4"

count=-2
old_count=-1
while [[ $count != $old_count ]]
do
	[[ "$SPARUL_FILES" == '' ]] && SPARUL_FILES=$(ls "$my_lib/common-rules/"*.sparul)
	echo "$SPARUL_FILES" | xargs -n 1 "$my_lib/map-single-rule.sh" "$tdb_file"
	
	old_count=$count
	echo "SELECT (COUNT(*) AS ?ct) { GRAPH ${TARGET_GRAPH} { ?s ?p ?o} }" \
	  | "$JENA_HOME/bin/tdbquery" --loc="$tdb_file" --query=- --results=tsv \
		| tail -n 2

	set -x
	count=$(echo "SELECT (COUNT(*) AS ?ct) { GRAPH ${TARGET_GRAPH} { ?s ?p ?o} }" \
	  | "$JENA_HOME/bin/tdbquery" --loc="$tdb_file" --query=- --results=tsv \
		| tail -n 2)
	set +x
done

[[ -z "$dump_file" ]] && exit

echo -e "\n\n\tDumping to '$dump_file'\n"

cat <<EOT | "$JENA_HOME/bin/tdbquery" --loc="$tdb_file" --query=- >"$dump_file"
CONSTRUCT { ?s ?p ?o }
WHERE { GRAPH ${TARGET_GRAPH} {?s ?p ?o} }
EOT
