import json, urllib.request, csv
from sys import stderr

js_all_wheat_runs = urllib.request.urlopen ( rna_api_base + "/json/0/getRunsByOrganism/triticum_aestivum" ).read()
js_all_wheat_runs = json.loads ( js_all_wheat_runs )
exp_accs = { row [ "STUDY_ID" ] for row in js_all_wheat_runs }

# TODO:
