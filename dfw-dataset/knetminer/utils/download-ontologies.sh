set -e # Stop upon error
target_dir="$ELT_OUT/knetminer"

function get_file
{
	label="$1"
	url="$2"
	fpath="$3"
	
	echo -e "-- $label"
	wget "$url" -O "$target_dir/$fpath"
}

echo -e "\n\n\tDownloading Schema/ontology files"

mkdir -p "$target_dir/ontologies"

get_file 'BioKNO main file' \
  https://raw.githubusercontent.com/Rothamsted/bioknet-onto/master/bioknet.owl ontologies/bioknet.owl
get_file 'BioKNO Ondex mappings' \
  https://raw.githubusercontent.com/Rothamsted/bioknet-onto/master/bk_ondex.owl ontologies/bk_ondex.owl
get_file 'Mappings to external ontologies' \
	https://raw.githubusercontent.com/Rothamsted/bioknet-onto/master/bk_mappings.ttl ontologies/bk_mappings.ttl

get_file "schema.org" http://schema.org/version/latest/schema.ttl ontologies/schema.ttl

# TODO: bioschemas!
get_file "BioPAX" http://www.biopax.org/release/biopax-level3.owl ontologies/biopax-level3.owl
get_file "SIO" http://semanticscience.org/ontology/sio.owl ontologies/sio.owl
get_file "dcterms:" \
  http://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl \
	ontologies/dcterms.ttl
get_file "dc:" \
	http://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_elements.ttl \
	ontologies/dcelements.ttl
get_file "SKOS" http://www.w3.org/TR/skos-reference/skos.rdf ontologies/skos.rdf
