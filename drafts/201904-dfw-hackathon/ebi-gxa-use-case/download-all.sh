while [[ $# -gt 0 ]]
do
	opt_name="$1"
  case $opt_name in
  	# WARNING: these '--:' special markers are used by --help to generate explanations about the available
  	# options.
  	#--: Skips the step about experiments metadata
  	--no-ae) is_ae=false; shift;;
  	#--: Skips the step about GXA expression levels
  	--no-gxa) is_gxa=false; shift;;
  	#--: Skips the step about condition annotations
  	--no-cond) is_cond=false; shift;;
  	#--: This message
  	--help)
      echo -e "\n\n\t$(basename $0) [options]\n"

  		# Report the options
  		egrep -i '(#\-\-:|\-\-[a-z].+\))' "$0" | sed s/'#\-\-:/#/g' | sed -E s/'(^\s+\-\-.+)\)'/'\1'/g
      echo ""

      exit 1;;
    --*)
      echo -e "\n\n\tInvalid option '$1', try --help\n"
      exit 1;;
  	*)
  		shift;;
	esac
done



for specie in arabidopsis wheat
do
  if [[ $is_ae != false ]]; then
    echo -e "\n\n\texperiments/$specie"
    python3 ae-download.py $specie <gxa-$specie-exps.tsv >data/$specie-exp.ttl &
  fi

  if [[ $is_gxa != false ]]; then
    echo -e "\n\n\tresults/$specie"
	  python3 gxa-download.py <gxa-$specie-exps.tsv >data/$specie-ge.ttl &
  fi
done

if [[ $is_cond != false ]]; then
  echo -e "\n\n\tconditions"
  cat gxa-*-exps.tsv | python3 gxa-conditions-download.py >data/gxa-conditions.ttl &
fi

echo -e "\n\n\tAll download jobs launched, waiting to finish"
wait $(jobs -p)
echo -e "The End"
