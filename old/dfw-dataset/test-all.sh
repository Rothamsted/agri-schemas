cd "$(dirname "$0")"

echo -e "\n\n  ------ Testing Agrischemas Pipeline ---------\n"

#pytest -v --ignore-glob='*/etl-tools/*' .

find `pwd` -name '*_test.py' -not -path '*etl-tools*' \
  | xargs python3 -m unittest -v
