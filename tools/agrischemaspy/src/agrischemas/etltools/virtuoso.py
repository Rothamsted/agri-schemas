"""
Utilities for Virtuoso-based SPARQL endpoints.

"""

from luqum.parser import parser
from luqum.tree import (AndOperation, BoolOperation, Boost, Fuzzy, Group, Not,
                        OrOperation, Phrase, Range, SearchField,
                        UnknownOperation, Word)
from luqum.utils import UnknownOperationResolver


def lucene_to_bif_contains ( query: str ) -> str:
	"""
	Translates the basics of a Lucene query into a Virtuoso `bif:contains` expression.

	We have written this to interface generic text search components with Virtuoso endpoints. 
  **WARNING**: it only supports the most common Lucene syntax constructs, since the Virtuoso 
	counterpart is much more limited. See the tests to get an idea.

	WARNING: though partially tested, the code was mostly copy-pasted from ChatGPT.
	"""	
	def quote_term ( term: str ) -> str:
		"""
		Normalises a Lucene term or phrase into a Virtuoso-safe quoted token.
		"""

		# Strip surrounding double quotes (Lucene phrases)
		if len(term) >= 2 and term[0] == '"' and term[-1] == '"':
			term = term[1:-1]

		# Strip surrounding single quotes if user typed them
		if len(term) >= 2 and term[0] == "'" and term[-1] == "'":
			term = term[1:-1]

		# Escape single quotes for Virtuoso
		term = term.replace("'", "''")

		return f"'{term}'"


	def translate ( node ):
		"""
		AST-based translation. 
		"""
		# BoolOperation (AND/OR/NOT with multiple children)
		if isinstance(node, BoolOperation):
			op = node.op.upper()
			if not op: op = "AND"
			children = [translate(child) for child in node.children]
			return f" {op} ".join(f"({c})" for c in children)

		# Explicit AND
		if isinstance(node, AndOperation):
			left = translate(node.children[0])
			right = translate(node.children[1])
			return f"({left}) AND ({right})"

		# Implicit AND
		if isinstance(node, UnknownOperation):
			children = [translate(child) for child in node.children]
			result = children[0]
			for child in children[1:]:
				result = f"({result}) AND ({child})"
			return result

		# OR
		if isinstance(node, OrOperation):
			left = translate(node.children[0])
			right = translate(node.children[1])
			return f"({left}) OR ({right})"

		# NOT (optional)
		if isinstance(node, Not):
			child = translate(node.children[0])
			return f"NOT ({child})"

		# Group (...)
		if isinstance(node, Group):
			return f"({translate(node.children[0])})"

		# Word
		if isinstance(node, Word):
			return quote_term(node.value)

		# Phrase
		if isinstance(node, Phrase):
			return quote_term(node.value)

		# Reject unsupported features
		if isinstance(node, (SearchField, Range, Fuzzy, Boost)):
			raise ValueError (
				f"Unsupported Lucene feature: {type(node).__name__}"
			)

		raise ValueError ( f"Unsupported node: {type(node)}" )
	
	ast = parser.parse(query)
	# Does some simplifications, eg, a b c -> a AND b AND c, without binary compositions.
	resolver = UnknownOperationResolver ( resolve_to = BoolOperation )
	ast = resolver.visit(ast)
	return translate(ast)
