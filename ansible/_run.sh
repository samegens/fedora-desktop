#!/bin/bash

set -uo pipefail

if [ "$#" -lt 2 ]; then
    echo "Usage: _run.sh <playbook> <server name> <ansible-playbook arguments>"
	exit 1
fi

# First make sure that we run ansible-playbook in the directory of this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

PLAYBOOK=$1
shift
SERVER_NAME=$1
shift

# Use timestamped log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="/var/log/ansible"
LOG_FILE="$LOG_DIR/${TIMESTAMP}_${SERVER_NAME}_$(basename $PLAYBOOK .yml).log"
echo "Logging to ${LOG_FILE}"

# Set the log path for this run
export ANSIBLE_LOG_PATH="$LOG_FILE"

# Run ansible-playbook and capture exit code
ansible-playbook $PLAYBOOK -v --diff --limit $SERVER_NAME "$@"
EXIT_CODE=$?

# Generate summary if log file exists
if [ -f "$LOG_FILE" ]; then
    echo ""
    python3 "$DIR/summarize_log/summarize_log.py" "$LOG_FILE"
fi

exit $EXIT_CODE
