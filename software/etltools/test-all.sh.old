cd "$(dirname "$0")"

echo -e "\n\n  ------ Testing ETL Tools ---------\n"

err=0
for py in $(find . -type f -name '*-test.py')
do 
	echo "'$py'"
	python3 "$py"
	myerr=$?
	[[ $err == 0 ]] && [[ $myerr != 0 ]] && err=1
	out="$out\n$py\t[$([[ $myerr == 0 ]] && echo 'OK' || echo 'KO')]"
done

echo -e "\n\n ----- SUMMARY ------\n"
echo -e "$out" | column -t -s$'\t'
echo -e '\n  ' $([[ $err == 0 ]] && echo 'ALL TESTS PASSED' || echo 'THERE ARE TEST FAILURES') '\n'
exit $err
