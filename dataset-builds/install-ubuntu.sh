
printf "\n\n  Installing Python\n"
# TODO

printf "\n\n  Installing Virtuoso\n"
# TODO

printf "\n\n  Installing rdfutils/virtuoso-utils\n"
cd "$RDFUTILS_HOME/.."
git clone https://github.com/marco-brandizi/rdfutils.git "$(basename rdfutils)"

printf "\n\n  Changing Virtuoso service to point to "$VIRTUOSO_DATA_DIR"\n"
TODO
