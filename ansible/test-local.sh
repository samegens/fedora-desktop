#!/bin/bash
set -xueo pipefail

ansible-playbook test.yml -v --limit localhost "$@"
