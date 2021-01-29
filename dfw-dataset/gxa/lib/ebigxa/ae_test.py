import unittest
import io, csv
from ebigxa.ae import rnaseqer_experiments_download, ae_accessions_filter

#etltools.utils.logger_config()
#log = logging.getLogger ( __name__ )

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
		accs = [ 'STUDY_ID', 'E-MTAB-7978', 'DRP003686', 'E-GEOD-102988', 'E-GEOD-38600', 'DRP004436', 'ERP005565' ]
		accs = [ [ a ] for a in accs ]
		accs = [ a for a in ae_accessions_filter ( accs ) ]
		#print ( accs )
		self.assertTrue ( "E-MTAB-7978" in accs, "Probe study not found in filtered accessions!" )
		self.assertFalse ( "DRP003686" in accs, "Unexpected study found in filtered accessions!" )
		
		
if __name__ == '__main__':
	unittest.main()
