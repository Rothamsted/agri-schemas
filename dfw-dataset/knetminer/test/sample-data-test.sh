if [[ "$DFW_ELT" == "" ]]; then
  cat <<EOT


	DFW_ELT isn't defined! You need to instantiate an environment, with something like:
		
		. <some-file>-env.sh

EOT
	exit 1
fi

. "$DFW_ELT/namespaces.sh"

echo -e "--- Generating test RDF"
sample_rdf=/tmp/knetminer-sample.ttl
"$ODX2RDF"/odx2rdf.sh $ODX2RDF/examples/text_mining.oxl "$sample_rdf"


echo -e "--- Loading test RDF into TDB"
test_tdb=/tmp/knetminer-mapping-test-tdb
rm -Rf "$test_tdb"
"$JENA_HOME/bin/tdbloader" --loc="$test_tdb" "$ELT_OUT/knetminer/ontologies/"* "$sample_rdf"


echo -e "--- Running Agrischemas mappings"
mapping_out="/tmp/knetminer-mapping-test-out.ttl"
"$ELT_TOOLS/sparul-mapping/sparul-mapping.sh" "$test_tdb" 'schema:' "<$(ns agGraph)knetminer-sample>" "$mapping_out"

testSchemaName ()
{
  { 
		cat <<EOT 
			$(sparql_ns)

			PREFIX bk:  <http://knetminer.org/data/rdf/terms/biokno/>

			ASK {
				BIND ( "Probable trehalose-phosphate phosphatase 1" AS ?testName )
				?protein bk:prefName ?testName; schema:name ?testName.
			}
EOT
	} | assert_sparql "schema:name not inferred from bk:prefName!"
}

. "$(which shunit2)"
