from os import path, remove
from sys import stderr
from etltools.utils import DEFAULT_NAMESPACES, get_jena_home
import glob
import re
import sh

def map_rule ( 
	tdb_path, sparql_rule, rule_name = None, dump_file = None,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	jena_home = get_jena_home ()

	rule_name = extract_rule_name ( sparql_rule, rule_name )
	if not rule_name: rule_name = '<Unknown>'

	# resolve placeholders
	for key in sparql_vars:
		sparql_rule = sparql_rule.replace ( "${%s}" % key, sparql_vars [ key ] )

	if namespaces:
		sparql_rule = namespaces.to_sparql () + "\n" + sparql_rule
		
	print ( f"Applying '{rule_name}'", file = stderr )
	
	tdb_sh = sh.Command ( jena_home + "/bin/tdbquery" )
	try:
		sh.awk (
			tdb_sh ( "--loc=%s" % tdb_path, "--results=tsv", "--query=-", _piped = True, _in = sparql_rule ),
			'NR > 1 { print $0 "." }', _out = dump_file
		);
	except Exception as ex:
		raise ChildProcessError ( "Error: while running the query:\n%s " % sparql_rule ) from ex


def map_from_rules ( 
	sparql_rules, tdb_path, dump_file_path = None, sparql_vars = {},
	namespaces = DEFAULT_NAMESPACES
):
	# Need to join partial results on a new file
	if ( dump_file_path ):
		if path.exists( dump_file_path ): remove ( dump_file_path )
	
	# TODO: if it's a dictionary, reorder based on keys	
	for rule in sparql_rules:
		rule_name = "?"
		if type ( rule ) is tuple: ( rule, rule_name ) = rule

		# Need to join partial results on a new file
		if ( dump_file_path ):
			with open ( dump_file_path, "a" ) as dump_file:
				map_rule ( tdb_path, rule, rule_name, dump_file, sparql_vars, namespaces )				
			continue
		
		# Else, we're dumping on stdout
		map_rule ( tdb_path, rule, rule_name, dump_file_path, sparql_vars, namespaces )				


def map_from_files ( 
	rule_paths, tdb_path, dump_file_path,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	rules = read_rules_from_files ( rule_paths )
		
	# Else, it's empty
	map_from_rules ( rules, tdb_path, dump_file_path, sparql_vars, namespaces )


def extract_rule_name ( sparql_rule, default = None ):
	nmatch = re.search ( "# Rule Name: (.+)$", sparql_rule, re.MULTILINE )
	if nmatch: return nmatch.group ( 1 )
	return default
	
"""
  If a rule has the same 'Rule Name' annotation of another met earlier, this is overridden
  by the new rule.
  
  TODO: overriding needs specific testing, for the moment it's used and tested in 
  knetminer tests. 
"""
def read_rules_from_files ( rule_paths ):
	named_rules = {}
	
	if type ( rule_paths ) is not list:
		rule_paths = [ rule_paths ]
	
	for rpath in rule_paths:
		rfiles = [ rpath ] if not path.isdir ( rpath ) \
		        else glob.glob ( rpath + "/*.sparql" ) 
		for rfile in rfiles:
			with open ( rfile, 'r' ) as hrule:
				rule_sparql = hrule.read ()
				rule_name = extract_rule_name ( rule_sparql, path.abspath ( rfile ) )
				if rule_name in named_rules:
					print ( "Overriding \"%s\"" % rule_name, file = stderr )
				named_rules [ rule_name ] = rule_sparql

	return [ (sparql, name) for (name, sparql) in named_rules.items() ]		
