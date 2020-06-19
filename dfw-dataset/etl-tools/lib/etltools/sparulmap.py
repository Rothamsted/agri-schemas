from os import path
from etltools.utils import DEFAULT_NAMESPACES, get_jena_home
from subprocess import run, PIPE
import glob
import re


def map_rule ( 
	tdb_path, sparul_rule, target_graph_spec, rule_name = None,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	jena_home = get_jena_home ()

	rule_name = extract_rule_name ( sparul_rule, rule_name )
	if not rule_name: rule_name = '<Unknown>'

	# resolve placeholders
	sparql_vars [ "TARGET_GRAPH" ] = target_graph_spec
	for key in sparql_vars:
		sparul_rule = sparul_rule.replace ( "${%s}" % key, sparql_vars [ key ] )

	if namespaces:
		sparul_rule = namespaces.to_sparql () + "\n" + sparul_rule

	print ( f"Applying '{rule_name}'" )
	proc = run ( 
		[ jena_home + "/bin/tdbupdate", "--loc=%s" % tdb_path, "--update=-" ], 
		input = sparul_rule,
		text = True
	)
	if proc.returncode != 0:
		raise ChildProcessError ( "Error #%d while running the query:\n%s " % ( proc.returncode, sparul_rule ) )


def map_from_rules ( 
	sparul_rules, tdb_path, target_graph_spec, dump_file_path = None,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	jena_home = get_jena_home ()
	
	count = -2
	old_count = -1
	iteration = 1
	while count != old_count:
		print ( "\n\t Iteration %s\n" % iteration )
		old_count = count
		for rule in sparul_rules:
			rule_name = "?"
			if type ( rule ) is tuple: ( rule, rule_name ) = rule
			map_rule ( tdb_path, rule, target_graph_spec, rule_name, sparql_vars, namespaces )

		# See the triples count
		ct_query = "SELECT (COUNT(*) AS ?ct) { GRAPH %s { ?s ?p ?o} }" % target_graph_spec
		if namespaces:
			ct_query = namespaces.to_sparql () + "\n" + ct_query

		proc = run ( 
			[ jena_home + "/bin/tdbquery", "--loc=%s" % tdb_path, "--query=-", "--results=tsv" ], 
			stdout = PIPE, input = ct_query, text = True
		)
		if proc.returncode != 0:
			raise ChildProcessError ( "Error #%d while running Jena TDB (triples count): " % proc.returncode )
		
		count = int ( proc.stdout.split ( '\n' ) [ -2 ] )
		iteration += 1

	if not dump_file_path: return
	
	print ( "Dumping to '%s'" % dump_file_path )

	dump_query = """
		CONSTRUCT { ?s ?p ?o }
		WHERE { GRAPH %s {?s ?p ?o} }
	""" % target_graph_spec
	if namespaces: dump_query = namespaces.to_sparql () + "\n" + dump_query

	with open ( dump_file_path, 'w' ) as df:
		proc = run ( 
			[ jena_home + "/bin/tdbquery", "--loc=%s" % tdb_path, "--query=-" ], 
			input = dump_query, stdout = df, text = True
		)
	if proc.returncode != 0:
		raise ChildProcessError ( "Error #%d while running Jena TDB (result dump) " % proc.returncode )


def map_from_files ( 
	rule_paths, tdb_path, target_graph_spec, dump_file_path,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	rules = read_rules_from_files ( rule_paths )
	map_from_rules ( rules, tdb_path, target_graph_spec, dump_file_path, sparql_vars, namespaces )


def extract_rule_name ( sparul_rule, default = None ):
	nmatch = re.search ( "# Rule Name: (.+)$", sparul_rule, re.MULTILINE )
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
		        else glob.glob ( rpath + "/*.sparul" ) 
		for rfile in rfiles:
			with open ( rfile, 'r' ) as hrule:
				rule_sparul = hrule.read ()
				rule_name = extract_rule_name ( rule_sparul, path.abspath ( rfile ) )
				if rule_name in named_rules:
					print ( "Overriding \"%s\"" % rule_name )
				named_rules [ rule_name ] = rule_sparul

	return [ (sparul, name) for (name, sparul) in named_rules.items() ]		
