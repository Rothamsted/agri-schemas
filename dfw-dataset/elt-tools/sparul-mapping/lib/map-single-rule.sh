tdb_file="$1"
sparul_file="$2"

cd "$(dirname $0)"

[[ -z '$NAMESPACES' ]] || sparql_ns=$(sparql_ns "$NAMESPACES")

# DEBUG 
query=$(eval "echo \"$sparql_ns\n$(cat "$sparul_file")\"")

echo $query | "$JENA_HOME/bin/tdbupdate" --loc="$tdb_file" --update=-

err=$?
[[ $err == 0 ]] && exit

echo -e "\n\nERROR while mapping with the query:\n$query\n"
exit $err
