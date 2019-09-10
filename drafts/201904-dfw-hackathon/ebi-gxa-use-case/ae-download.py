import csv, io
from urllib.request import urlopen
from utils import make_id, get_gxa_accessions, print_rdf_namespaces
from utils import rdf_str, rdf_pval, rdf_stmt
from textwrap import dedent

import sys

specie = sys.argv[ 1 ] if len ( sys.argv ) > 1 else ""
specie2terms = { 
	"arabidopsis": [ "http://purl.bioontology.org/ontology/NCBITAXON/3701" ],
	"wheat": [ "http://purl.bioontology.org/ontology/NCBITAXON/4565" ]
}
print ( "SPECIE:" + specie )

print_rdf_namespaces ()


# Process the IDF
for exp_acc in get_gxa_accessions():
	mage_tab_base = "https://www.ebi.ac.uk/arrayexpress/files/{0}/{0}.{1}.txt"
	idf_url = mage_tab_base.format ( exp_acc, "idf" )

	with urlopen ( idf_url ) as idf_stream:
		csv_reader = csv.reader ( io.TextIOWrapper ( idf_stream, encoding = 'utf-8' ), delimiter = "\t" )
		idf = { row [ 0 ]: row [ 1 ] for row in csv_reader }
	
		exp_acc = idf [ "Comment[ArrayExpressAccession]" ]
		idf [ "accession" ] = exp_acc # .format() has problems with the original key
		exp_pmid = idf.get ( "Pubmed ID" )
		idf [ "experiment" ] = "bkr:exp_" + exp_acc
		idf [ "publication" ] = "bkr:pmid_" + str ( exp_pmid )

		rdf_tpl = """
		{experiment} a bioschema:Study;
			agri:accession: "{accession}";
		"""
		rdf = dedent ( rdf_tpl.format (**idf) )

		def rdf_adder ( fields ):
			rdf = ""
			for (key, rdf_prop) in fields.items ():
				rdf += rdf_str ( idf, key, "\t" + rdf_prop )
			return rdf

		rdf += rdf_adder ( { 
			"Investigation Title": "dc:title",
			"Experiment Description": "schema:description",
			"Public Release Date": "schema:datePublished",
			"Pubmed ID": "agri:pmedId",
		})

		specie_terms = specie2terms.get ( specie )
		if specie_terms:
			specie_literals = "[ " + ", ".join ( [ "<" + s + ">" for s in specie_terms ] ) + " ]"
			rdf += "\tschema:additionalProperty: " + specie_literals + ";\n"

		rdf += ".\n"

		if exp_pmid:
			rdf += "\n"
			rdf += "{publication} a agri:ScholarlyPublication\n".format ( **idf )
			rdf += rdf_adder ({
				"Publication Title": "dc:title",
				"Pubmed ID": "agri:pmedId"
			})
			rdf += ".\n"
		
		print ( rdf )
	# /end: idf_stream
# /end: exp_acc loop
