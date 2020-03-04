# Use this prolog to go to the script's directory
mydir="$(pwd)"
cd "$(dirname ${BASH_SOURCE[0]})"

export DFW_ELT="$(pwd)"
export ELT_OUT="$DFW_ELT/output"
export ELT_TOOLS="$DFW_ELT/elt-tools"

# These are needed for tests
export ODX2RDF="$HOME/Documents/Work/RRes/ondex_git/ondex-full/ondex-knet-builder/modules/rdf-export-2-cli/target/rdf-export-2-cli_2.1.2-SNAPSHOT"

# Other defs in subsystems
. "$ELT_TOOLS/brandizi-env.sh"

# Since you're sourcing me (". $0"), you typically want to go back to the initial workdir
cd "$mydir"
