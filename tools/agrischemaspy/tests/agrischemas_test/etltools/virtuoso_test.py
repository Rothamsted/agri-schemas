import pytest
from agrischemas.etltools.virtuoso import lucene_to_bif_contains, UnsupportedLuceneFeature

from logging import getLogger
log = getLogger ( __name__ )

@pytest.mark.parametrize (
	"lucene, expected",
	[
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
	"lucene",
	[
		"title:disease",
		'"foo bar"~3',
		"foo~",
		"foo^2",
		"[a TO b]",
	],
)
def test_lucene_to_bif_contains_unsupported_features(lucene):
	with pytest.raises(UnsupportedLuceneFeature):
		lucene_to_bif_contains(lucene)
