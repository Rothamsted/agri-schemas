import os
from os.path import dirname, abspath, exists
import unittest

def run_workflow ():

	mydir = dirname ( abspath ( __file__ ) )
	
	os.chdir ( mydir )
	
	if os.system ( "snakemake --snakefile getfiles.snakefile --configfile getfiles-test-cfg.yaml" ) != 0:
		raise ChildProcessError ( "Download workflow execution failed" )
	
class GetFilesTest ( unittest.TestCase ):
	is_initialized = False
	
	def __init__ ( self, methodName ):
		if not GetFilesTest.is_initialized:
			run_workflow ()
			GetFilesTest.is_initialized = True
		super().__init__ ( methodName )	

	def test_dcterms_out ( self ):
		self.assertTrue ( exists ( "/tmp/etl-tools/ontologies/dcterms.ttl" ), "dcterms.ttl not created!" )
	
	def test_schema_out ( self ):
		self.assertTrue ( exists ( "/tmp/etl-tools/ontologies/schema.ttl" ), "schema.ttl not created!" )

if __name__ == '__main__':
	unittest.main()
