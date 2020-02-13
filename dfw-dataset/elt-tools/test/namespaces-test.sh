cd "$(dirname "$0")"
cd ..
. ./namespaces.sh

function test_init ()
{
	assertFalse "NAMESPACES not defined!" "[[ -z '$NAMESPACES' ]]"

  assertTrue "schema: not found!!" \
		"[[ '$NAMESPACES' =~ '@prefix schema: <http://schema.org/>.' ]]"

	assertTrue "rdfs: not found!" \
		"[[ '$NAMESPACES' =~ '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.' ]]"
}

function test_ns ()
{
	assertEquals "ns() didn't work!" "http://schema.org/" "$(ns schema)"
}

function test_sparql_ns ()
{
	nss="$(sparql_ns)"

  assertTrue "sparql_ns didn't work (schema:)!" \
		"[[ '$nss' =~ 'PREFIX schema: <http://schema.org/>' ]]"
  
	assertTrue "sparql_ns didn't work (rdfs:)!" \
		"[[ '$nss' =~ 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>' ]]"
}

. "$(which shunit2)"
