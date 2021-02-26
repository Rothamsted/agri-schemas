for v in ETL_OUT ETL_TMP
do
	[[ -z "`echo $v`" ]] && "$v unset, please source some *-env.sh file to setup my environment" && exit 1
done

for f in "$ETL_OUT/rdf/gxa" "$ETL_TMP/gxa"
do
	echo "Deleting \"$f\""
	rm -Rf "$f"
done

