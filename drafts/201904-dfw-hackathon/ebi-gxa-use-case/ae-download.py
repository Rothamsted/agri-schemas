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

print_rdf_namespaces ()


# Process the IDF, the MAGETAB file that describes the experiment
for exp_acc in get_gxa_accessions():
	mage_tab_base = "https://www.ebi.ac.uk/arrayexpress/files/{0}/{0}.{1}.txt"
	idf_url = mage_tab_base.format ( exp_acc, "idf" )

	with urlopen ( idf_url ) as idf_stream:
		csv_reader = csv.reader ( io.TextIOWrapper ( idf_stream, encoding = 'utf-8' ), delimiter = "\t" )
		# we need to normalise keys to lower case, cause they're used inconsinstently sometimes
		idf = { row [ 0 ].lower (): row [ 1 ] for row in csv_reader }

		exp_acc = idf [ "comment[arrayexpressaccession]" ]
		idf [ "accession" ] = exp_acc # .format() has problems with the original key
		idf [ "experiment" ] = "bkr:exp_" + exp_acc
		exp_pmid = idf.get ( "pubmed id" ) 
		if exp_pmid: idf [ "publication" ] = "bkr:pmid_" + str ( exp_pmid )

		rdf_tpl = """
		{experiment} a bioschema:Study;
			schema:identifier "{accession}";
		"""
		rdf = dedent ( rdf_tpl.format (**idf) )

		# Facility to add IDF fields to the RDF
		# fields is a map of original field -> RDF property
		def rdf_adder ( fields ):
			rdf = ""
			for (key, rdf_prop) in fields.items ():
				rdf += rdf_str ( idf, key, "\t" + rdf_prop )
			return rdf

		rdf += rdf_adder ( { 
			"investigation title": "dc:title",
			"experiment description": "schema:description",
			"public release date": "schema:datePublished"
		})
		if exp_pmid: rdf += "\tschema:about {publication};\n".format ( **idf )

		specie_terms = specie2terms.get ( specie )
		if specie_terms:
			specie_literals = ", ".join ( [ "<" + s + ">" for s in specie_terms ] )
			rdf += "\tschema:additionalProperty " + specie_literals + ";\n"

		rdf += ".\n"

		if exp_pmid:
			rdf += "\n"
			rdf += "{publication} a agri:ScholarlyPublication;\n".format ( **idf )
			rdf += rdf_adder ({
				"publication title": "dc:title",
				"pubmed id": "agri:pmedId",
				"publication author list": "agri:authorsList"
			})
			rdf += ".\n"
		
		print ( rdf )
	# /end: idf_stream
# /end: exp_acc loop
