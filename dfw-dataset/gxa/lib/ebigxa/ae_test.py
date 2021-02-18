import unittest
import io, csv
from etltools.utils import logger_config
from ebigxa.ae import rnaseqer_experiments_download, ae_accessions_filter, rnaseqer_experiments_download_all, rdf_ae_experiments

log = logger_config ( __name__ )

class AeTest ( unittest.TestCase ):
	
	ae_exps = None
	
	@classmethod
	def setUpClass(cls):
		out = io.StringIO ()
		rnaseqer_experiments_download ( "arabidopsis_thaliana", out )
		outs = out.getvalue ()
		inh = io.StringIO ( outs, newline = None )
		cls.ae_exps = list ( csv.reader ( inh, delimiter = "\t" ) )

	def test_rna_experiments_dowbload ( self ):
		accs = [ row [ 0 ] for row in AeTest.ae_exps ]
		self.assertTrue ( "STUDY_ID" in accs, "Header not found in the result!" )
		self.assertTrue ( "E-MTAB-1946" in accs, "Probe study not found in the result!" )

	def test_accessions_filter ( self ):
		# Mockup list, the real one is too long
		accs = [ 'STUDY_ID', 'E-MTAB-7978', 'DRP003686', 'E-GEOD-102988', 'E-GEOD-38600', 'E-MTAB-4289', 'DRP004436', 'ERP005565' ]
		accs = [ [ a ] for a in accs ]
		results = [ row for row in ae_accessions_filter ( accs ) ]
		accs = [ row [ 0 ] for row in results ]
		log.debug ( "ae_accessions_filter() result:\n%s", results )
		self.assertTrue ( ( "E-MTAB-7978", [ "RNASeq" ] ) in results, "Probe study not found in filtered accessions!" )
		self.assertTrue ( ( "E-MTAB-4289", [ "DEX" ] ) in results, "Probe study not found in filtered accessions!" )
		self.assertFalse ( "DRP003686" in accs, "Unexpected study found in filtered accessions!" )
		
	"""
		WARNING: it runs for long time
	"""
	def _test_rnaseqer_experiments_download_all ( self ):
		out = io.StringIO ()
		rnaseqer_experiments_download_all ( [ "triticum_aestivum" ], out )
		outs = out.getvalue ()
		inh = io.StringIO ( outs, newline = None )
		exps = list ( csv.reader ( inh, delimiter = "\t" ) )
		log.info ( "EXPS:\n%s", exps )
		self.assertTrue ( ['E-GEOD-38344', 'RNASeq'] in exps, "Probe study not found by the all-downloader!" )
		self.assertTrue ( ['E-MTAB-4245', 'DEX'] in exps, "Probe study not found by the all-downloader!" )
		
		
	def test_rdf_ae_experiments ( self ):
		accs = [ 'E-MTAB-7978', 'E-MTAB-4289' ]
		out = io.StringIO ()
		rdf_ae_experiments ( accs, out )
		outs = out.getvalue ()
		log.info ( "rdf_ae_experiments() test output (truncated):\n%s\n\n", outs [ 0: 4000 ] )		
		
		
		
if __name__ == '__main__':
	unittest.main()
