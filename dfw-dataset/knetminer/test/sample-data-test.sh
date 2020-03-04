set -e # stop upon error

if [[ "$DFW_ELT" == "" ]]; then
  cat <<EOT


	DFW_ELT isn't defined! You need to instantiate an environment, with something like:
		
		. <some-file>-env.sh

EOT
	exit 1
fi

echo -e "--- Generating test RDF"
sample_rdf=/tmp/knetminer-sample.ttl
"$ODX2RDF"/odx2rdf.sh $ODX2RDF/examples/text_mining.oxl "$sample_rdf"


echo -e "--- Loading test RDF into TDB"
test_tdb=/tmp/knetminer-mapping-test-tdb
rm -Rf "$test_tdb"
"$JENA_HOME/bin/tdbloader" --loc="$test_tdb" "$ELT_OUT/knetminer/ontologies/"* "$sample_rdf"


echo -e "--- Running Agrischemas mappings"
mapping_out="/tmp/knetminer-mapping-test-out.ttl"
./sparul-mapping/sparul-mapping.sh "$test_tdb" 'schema:' "<$(ns graphs)knetminer-sample>" "$mapping_out"
