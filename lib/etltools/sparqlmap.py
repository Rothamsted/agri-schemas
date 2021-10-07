"""
	SPARQL Mapping Utilities
	
	These employ SPARQL CONSTRUCT to build RDF-to-RDF mapping.
	
	:author: Marco Brandizi
"""


from os import path, remove
from sys import stderr
from etltools.utils import DEFAULT_NAMESPACES, get_jena_home, XNamespaceManager
import glob
import re
import sh

"""
	Maps the RDF in a Jena TDB database into some other RDF using a CONSTRUCT statement defined
	by sparql_rule (see map-rules/ for examples)
	
	rule_name is optionally used for output messages.
	
	if dump_file is given, the output is sent there
	
	sparql_vars can be used to set up {placeholder}s in sparql_rule
	
	namespaces are prepended to the sparql_rule, or just ignored if set to None (as you see, we use a 
	default if not set)
	
	The output is a set of triples achieved by the rule, compatible with the .nt format
"""
def map_rule ( 
	tdb_path: str, sparql_rule: str, rule_name:  str = None, dump_file: str = None,
	sparql_vars: dict = {}, namespaces: XNamespaceManager = DEFAULT_NAMESPACES,
	compress = False
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
	
	try:
		tdb_sh = sh.Command ( jena_home + "/bin/tdbquery" )
		tdb_sh = tdb_sh ( "--loc=%s" % tdb_path, "--results=tsv", "--query=-", _piped = True, _in = sparql_rule )
		awk_str = 'NR > 1 { print $0 "." }'
		if not compress:
			sh.awk ( tdb_sh, awk_str, _out = dump_file );
		else:
			sh.bz2 ( sh.awk ( tdb_sh, awk_str, _piped = True ), _out = dump_file )
	except Exception as ex:
		raise ChildProcessError ( "Error: while running the query:\n%s " % sparql_rule ) from ex

"""
  map_rule() ran for multiple rules
"""
def map_from_rules ( 
	sparql_rules, tdb_path: str, dump_file_path: str = None, sparql_vars: dict = {},
	namespaces: XNamespaceManager = DEFAULT_NAMESPACES,
	compress = False
):
	# Need to join partial results on a new file
	if ( dump_file_path ):
		if path.exists( dump_file_path ): remove ( dump_file_path )
	
	for rule in sparql_rules:
		rule_name = "?"
		if type ( rule ) is tuple: ( rule, rule_name ) = rule

		# Need to join partial results on a new file
		if ( dump_file_path ):
			with open ( dump_file_path, "a" ) as dump_file:
				map_rule ( tdb_path, rule, rule_name, dump_file, sparql_vars, namespaces, compress )				
			continue
		
		# Else, we're dumping on stdout
		map_rule ( tdb_path, rule, rule_name, dump_file_path, sparql_vars, namespaces, compress )				

"""
  map_from_rules(), with the rules read from files.
  
  We need One rule (ie, SPARQL construct) per file in rule_paths directories.
  
  Rules can have metadata in SPARQL comments (see read_rules_from_files()).
"""
def map_from_files ( 
	rule_paths, tdb_path: str, dump_file_path: str,
	sparql_vars: dict = {}, namespaces: XNamespaceManager = DEFAULT_NAMESPACES,
	compress = False
):
	rules = read_rules_from_files ( rule_paths )	
	map_from_rules ( rules, tdb_path, dump_file_path, sparql_vars, namespaces, compress )


"""
	See read_rules_from_files()	 
"""
def extract_rule_name ( sparql_rule: str, default = None ):
	nmatch = re.search ( "# Rule Name: (.+)$", sparql_rule, re.MULTILINE )
	if nmatch: return nmatch.group ( 1 )
	return default
	
"""
	Used by map_from_files().
	
	SPARQL-based rules are read from the rule_paths directores.

  If a rule has the same 'Rule Name' annotation of another met earlier, this is overridden
  by the new rule.
  
  TODO: overriding needs specific testing, for the moment it's used and tested in 
  knetminer tests. 
"""
def read_rules_from_files ( rule_paths ):
	named_rules = {} # name -> sparql
	# Paths are needed to re-order based on them
	paths_2_names = {} # file path -> name
	names_2_paths = {} # name -> file path
	
	if type ( rule_paths ) is not list:
		rule_paths = [ rule_paths ]
	
	for rpath in rule_paths:
		rfiles = [ rpath ] if not path.isdir ( rpath ) \
		        else glob.glob ( rpath + "/*.sparql" ) 
		for rfile in rfiles:
			rule_path = path.abspath ( rfile );
			with open ( rfile, 'r' ) as hrule:
				rule_sparql = hrule.read ()
				rule_name = extract_rule_name ( rule_sparql, rule_path )
				
				if rule_name in named_rules:
					print ( "Overriding \"%s\"" % rule_name, file = stderr )
					del paths_2_names [ names_2_paths [ rule_name ] ]
				
				named_rules [ rule_name ] = rule_sparql
				paths_2_names [ rule_path ] = rule_name
				names_2_paths [ rule_name ] = rule_path
				
	sorted_paths = sorted ( paths_2_names )
	sorted_names = [ paths_2_names [ path ] for path in sorted_paths ]
	return [ (named_rules [ name ], name) for name in sorted_names ]		
