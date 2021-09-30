cd "$(dirname "$0")"

echo -e "\n\n  ------ Testing ETL Tools ---------\n"
python3 -m unittest discover -v --pattern "*_test.py" ./lib
