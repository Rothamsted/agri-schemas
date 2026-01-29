set -e
cd "$(dirname "$0")/.."
. ./init-env.sh

cd "${RDFUTILS_HOME}/virtuoso-utils"

bkg_prefix="http://knetminer.org/data/rdf/resources/graphs/"
for data_spec in gxa:gxaAgriSchemas
do
	IFS=':' read -r data_src_name ng_name <<< "$data_spec"
	data_src_dir="${ETL_OUT}/${data_src_name}"
	named_graph="${bkg_prefix}${ng_name}"

	printf "==| Loading from "${data_src_dir}" into named graph ${named_graph}\n"
	./virt_load.sh "${data_src_dir}" "${named_graph}"
done
