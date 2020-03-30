cd "$(dirname $0)"
my_dir="$(pwd)"

cd ../..
. ./namespaces.sh
. ./test/test-utils.sh

test_tdb=/tmp/sparul-mapping-test-tdb
rm -Rf "$test_tdb"
"$JENA_HOME/bin/tdbloader" --loc="$test_tdb" "$my_dir/test-data.ttl" 

./sparul-mapping/sparul-mapping.sh "$test_tdb" 'schema:' "<$(ns ex)mappedGraph>" /tmp/sparul-mapping-test.ttl

testTransitiveClass ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:b a ex:A } }" \
	  | assert_sparql "$test_tdb" "ex:b a ex:A not inferred!"
}

testMappedClass ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:a a schema:Thing } }" \
	  | assert_sparql "$test_tdb" "ex:a direct owl:equivalentClass not mapped!"
}

testMappedClassViaChain ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:b a schema:Thing } }" \
	  | assert_sparql "$test_tdb" "ex:b owl:equivalentClass/rdfs:subClassOf not mapped!"
}

testTransitiveProp ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:container ex:hasPart ex:specialComponent } }" \
	  | assert_sparql "$test_tdb" "ex:container ex:hasPart ex:specialComponent not inferred!"
}


testMappedProperty ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:a schema:sameAs ex:b } }" \
	  | assert_sparql "$test_tdb" "ex:a direct owl:equivalentProperty not mapped!"
}

testMappedPropertyViaChain ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:c schema:sameAs ex:b } }" \
	  | assert_sparql "$test_tdb" "ex:c direct owl:equivalentClass/rdfs:subClassOf not mapped!"
}

testMappedPropertyViaInverse ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:component schema:partOf ex:container } }" \
	  | assert_sparql "$test_tdb" "inverseOf-based mapping not working!"
}

testMappedPropertyViaInverseAndChain ()
{
	echo "$(sparql_ns) ASK { GRAPH ex:mappedGraph { ex:specialComponent schema:partOf ex:container } }" \
	  | assert_sparql "$test_tdb" "mapping based on subproperty+inverse not working!"
}

. "$(which shunit2)"
