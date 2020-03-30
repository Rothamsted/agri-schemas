[[ -z "$DFW_ELT" ]] && {
	echo -e "\n\n\tDFW_ELT isn't defined! Source some ***-env.sh file before me!\n"
	exit 1
}

cd "$(dirname $0)"

. "$DFW_ELT/namespaces.sh"
. "$ELT_TOOLS/test/test-utils.sh"
export TEST_TDB="$ELT_OUT/test/knetminer-test-tdb"

snakemake --snakefile sample-data-build.snakefile

# TODO: Rule about accession
# TODO: More tests

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
	} | assert_sparql "$TEST_TDB" "schema:name not inferred from bk:prefName!"
}


. "$(which shunit2)"
