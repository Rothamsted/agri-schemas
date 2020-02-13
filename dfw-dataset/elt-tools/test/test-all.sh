cd "$(dirname "$0")"
cd ..

err=0
for script in $(find $(pwd) -type f -name '*-test.sh')
do 
	echo "'$(basename $script)'"
	"$script"
	myerr=$?
	[[ $err == 0 ]] && [[ $myerr != 0 ]] && err=1
done

echo -e '\n\n\tTESTING' $([[ $err == 0 ]] && echo 'PASSED' || echo 'FAILED') '\n'
exit $err
