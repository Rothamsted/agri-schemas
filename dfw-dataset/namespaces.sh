if [[ "$DFW_ELT" == "" ]]; then
  cat <<EOT


	DFW_ELT isn't defined! You need to instantiate an environment, with something like:
		
		. <some-file>-env.sh

EOT
	exit 1
fi

. "$ELT_TOOLS/namespaces.sh"

export NAMESPACES="$NAMESPACES
@prefix agres: <http://agrischemas.org/resources/> .
@prefix aggraphs: <http://agrischemas.org/graphs/> .
"

