
function assert_sparql
{
  message=${1:-'SPARQL Test failed!'}
	result=$("$JENA_HOME/bin/tdbquery" --loc="$test_tdb" --query='-')
	assertTrue "$message" "[[ '$result' =~ 'Yes' ]]"
}
export -f assert_sparql
