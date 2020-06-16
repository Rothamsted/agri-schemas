cd "$(dirname "$0")"

echo -e "\n\n  ------ Testing Agrischemas Pipeline ---------\n"

pytest -v --ignore-glob='*/etltools/*' .
#python3 -m unittest discover -v --pattern "*_test.py" ./lib
