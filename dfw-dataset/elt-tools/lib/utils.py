import os, sys

ELT_OUT = os.getenv ( "ELT_OUT" )

if not ELT_OUT:
	print ( "\n\tERROR: ELT_OUT undefined, Initialise the environment with some ***-env.sh\n" )
	sys.exit ( 1 )
