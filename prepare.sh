#!/bin/bash

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi

apt-get update
apt-get upgrade -y

if [[ ! -f /usr/local/bin/pip3 ]]; then
    echo Installing pip...
    wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
    python3 /tmp/get-pip.py
fi

echo Installing Ansible...
python3 -m pip install ansible

echo
echo Make sure /root/.vault_pass contains the Ansible Vault password.
echo Then:
echo cd ansible
echo ./run.sh
