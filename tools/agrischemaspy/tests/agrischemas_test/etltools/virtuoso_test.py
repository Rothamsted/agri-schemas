from logging import getLogger

import pytest

from agrischemas.etltools.virtuoso import lucene_to_bif_contains

log = getLogger ( __name__ )

@pytest.mark.parametrize (
	argnames = "lucene, expected",
	ids = [ 
		"'*' wildcard", "OR/AND operators",
		"Phrase + implicit AND",
		"'?' + '*' wildcards", 
		"Implicit AND precedence" 
	],
	argvalues = [
		(
			"disease resist*",
			"('disease') AND ('resist*')",
		),
		(
			"(disease OR resistance) AND pathogen",
			"((('disease') OR ('resistance'))) AND ('pathogen')",
		),
		(
			'"disease resistance" pathogen',
			"('disease resistance') AND ('pathogen')",
		),
		(
			"foo? AND bar*",
			"('foo?') AND ('bar*')",
		),
		(
			# NOTE: this is the COMMON Lucene interpretation, the 'unknown' operator has LESS precedence
			# than OR
			"disease OR resistance pathogen",
			# therefore, this IS what to expect
			"(('disease') OR ('resistance')) AND ('pathogen')",
		),
	],
)
def test_lucene_to_bif_contains_supported_queries(lucene, expected):
	result = lucene_to_bif_contains (lucene)
	log.info ( f'Lucene: "{lucene}" -> Virtuoso: "{result}"' )
	assert result == expected


def test_lucene_to_bif_contains_multiple_implicit_and():
	lucene = "a b c"
	result = lucene_to_bif_contains (lucene)
	log.info ( f'Lucene: "{lucene}" -> Virtuoso: "{result}"' )
	assert result == "('a') AND ('b') AND ('c')"


@pytest.mark.parametrize(
	argnames = "lucene",
	ids = [ "Field search", "Proximity search", "Fuzzy search", "Boosting", "Range" ],
	argvalues = [
		"title:disease",
		'"foo bar"~3',
		"foo~",
		"foo^2",
		"[a TO b]",
	],
)
def test_lucene_to_bif_contains_unsupported_features(lucene):
	with pytest.raises(ValueError):
		lucene_to_bif_contains(lucene)
