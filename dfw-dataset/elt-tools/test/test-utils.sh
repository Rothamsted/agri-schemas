
function assert_sparql
{
	[[ $# < 2 ]] && {
		echo "assert_sparql requires a TDB database as first parameter"
		return 1
	}
  test_tdb="$1"
	message=${2:-'SPARQL Test failed!'}

	result=$("$JENA_HOME/bin/tdbquery" --loc="$test_tdb" --query='-')
	assertTrue "$message" "[[ '$result' =~ 'Yes' ]]"
}
export -f assert_sparql
