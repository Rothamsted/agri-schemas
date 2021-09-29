import os
from gxa_common import get_gxa_down_url, get_gxa_accessions

# Quick test to count the no. of genes involved in GXA expression levels
#

for exp_acc in get_gxa_accessions ():
	gxa_down_url = get_gxa_down_url ( exp_acc )
	os.system( "wget -O - \"%s\" | wc -l" % gxa_down_url)
