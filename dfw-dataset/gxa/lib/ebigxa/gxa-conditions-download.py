import urllib.parse, urllib.request, json, re
from textwrap import dedent
from gxa_common import process_gxa_experiments, make_condition_uri
from utils import print_rdf_namespaces

def get_term_accession ( uri ):
	bits = re.split ( "[\\/,\#,\?]", uri )
	if not bits: return ""
	return bits [ -1 ]

# Gets ontology terms associated to a condition by means of the Bioportal Annotator
#
def annotate_condition ( cond_label ):
	agrold_url = "http://services.agroportal.lirmm.fr/annotator/?"
	agrold_url += "longest_only=false&exclude_numbers=false&whole_word_only=true&exclude_synonyms=false&expand_mappings=false&negation=false&temporality=false&lemmatize=false&display_links=false&display_context=false"
	agrold_url += "&apikey=1de0a270-29c5-4dda-b043-7c3580628cd5"
	agrold_url += "&ontologies=" + urllib.parse.quote ( "AEO,AFO,EO,PO,TO,CO_121,CO_321" )
	agrold_url += "&text=" + urllib.parse.quote ( cond_label )
	
	js = urllib.request.urlopen ( agrold_url ).read()
	js = json.loads ( js )
	onto_term_uris = { ann [ "annotatedClass" ] [ "@id" ] for ann in js }
	return onto_term_uris


# The main: gets gene expression data to collect conditions from them
#
conditions = set()
process_gxa_experiments ( lambda exp_acc, gene_id, condition, tpm: conditions.add ( condition ) )

print_rdf_namespaces ()

knet_prefixes = {
  "TO": "http://knetminer.org/data/rdf/resources/trait_",
  "PO": "http://knetminer.org/data/rdf/resources/plantontologyterm_"	
}

# Now, take the collected conditions and build onto-term annotations
#
for cond_label in conditions:
	cond_uri = make_condition_uri ( cond_label )
	for term_uri in annotate_condition ( cond_label ):
		
		print ( "%s dc:type <%s>." % ( cond_uri, term_uri ) )
		
		# Add the accession
		acc = get_term_accession ( term_uri )
		if not acc: continue

		print ( "<%s> schema:identifier \"%s\"." % ( term_uri, acc ) )

		# Add links to Knetminer
		if not acc [ 2 ] == '_': continue
		id = acc [ 3: ]
		if not ( id and id.isdigit() ): continue
		onto_id = acc [ 0: 2 ]
		if not onto_id in knet_prefixes: continue
		knet_uri = knet_prefixes [ onto_id ] + acc.lower()
		print ( "%s dc:type <%s>." % ( cond_uri, knet_uri ) )
		print ( "<%s> schema:sameAs <%s>." % ( knet_uri, term_uri ) )
	print ()