import unittest
import io
from ebigxa.ae import rnaseqer_experiments_download

class AeTest ( unittest.TestCase ):
	
	def __init__ ( self, methodName ):
		super().__init__ ( methodName )	

	def test_rna_experiments_dowbload ( self ):
		with io.StringIO() as out:
			rnaseqer_experiments_download ( "arabidopsis_thaliana", out )
			out = out.getvalue ()
			
			self.assertTrue ( "Header not found in the result!", "STUDY_ID" in out )
			self.assertTrue ( "Probe study not found in the result!", "E-MTAB-1946" in out )

if __name__ == '__main__':
	unittest.main()
