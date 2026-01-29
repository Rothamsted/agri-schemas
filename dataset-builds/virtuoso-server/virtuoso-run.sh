# This IS NOT used on virtuoso-dev, since we decided to keep the Ubuntu installation, including
# systemd wrapping
#
set -e
cd "$(dirname "$0")/.."
. ./init-env.sh

mkdir -p "$ETL_VIRTUOSO_DATA_DIR/db"

virtuoso-t +foreground +wait +configfile "$ETL_HOME/environments/${KETL_ENV_ID}-virtuoso.ini" 
