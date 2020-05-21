import os
from etltools.utils import DEFAULT_NAMESPACES, get_jena_home
from subprocess import run, PIPE
import glob
import re


def map_rule ( 
	tdb_path, sparul_rule, target_graph_spec, rule_name = None,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	jena_home = get_jena_home ()

	nmatch = re.search ( "# Rule Name: (.+)$", sparul_rule, re.MULTILINE )
	if nmatch: rule_name = nmatch.group ( 1 )
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


def map ( 
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
			if type (rule) is tuple: ( rule, rule_name ) = rule
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
	rule_files_or_dir, tdb_path, target_graph_spec, dump_file_path,
	sparql_vars = {}, namespaces = DEFAULT_NAMESPACES
):
	rules = []
	if type ( rule_files_or_dir ) is not list:
		rule_files_or_dir = glob.glob ( rule_files_or_dir + "/*.sparul" )
	for frule in rule_files_or_dir:
		with open ( frule, 'r' ) as hrule:
			rules.append ( ( hrule.read (), frule ) )
	map ( rules, tdb_path, target_graph_spec, dump_file_path, sparql_vars, namespaces )
