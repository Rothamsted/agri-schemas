for specie in arabidopsis wheat
do
  echo -e "\n\n\texperiments/$specie"
  python3 ae-download.py $specie <gxa-$specie-exps.tsv >data/$specie-exp.ttl &

  echo -e "\n\n\tresults/$specie"
	python3 gxa-download.py <gxa-$specie-exps.tsv >data/$specie-ge.ttl &
done

echo -e "\n\n\tconditions"
cat gxa-*-exps.tsv | python3 gxa-conditions-download.py >data/gxa-conditions.ttl &

echo -e "\n\n\tAll download jobs launched, waiting to finish"
wait $(jobs -p)
echo -e "The End"
