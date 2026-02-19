#!/bin/bash
set -uexo pipefail

mkdir -p files/$1/ssh

yes | ssh-keygen -t ed25519 -C "sebastiaan@blauwe-lucht.nl" -f /tmp/$1 -N "" || true

cp -f /tmp/$1.pub ~/.ssh/
mkdir -p files/$1/ssh
mv /tmp/$1.pub files/$1/ssh/$1.pub
mkdir -p ~/Dropbox/git/homeserverconfig/ansible/files/$1/ssh
cp -f files/$1/ssh/$1.pub ~/Dropbox/git/homeserverconfig/ansible/files/$1/ssh/$1.pub

cp -f /tmp/$1 ~/.ssh
ansible-vault encrypt /tmp/$1
mv /tmp/$1 files/$1/ssh/$1
cp files/$1/ssh/$1 ~/Dropbox/git/homeserverconfig/ansible/files/$1/ssh/$1

echo "Don't forget to:"
echo "1. Add $1 to user_ssh_keys in tasks/ssh.yml"
echo "2. Add this block to the task 'Add entries to .ssh/config':"
echo "   Host $1"
echo "       IdentityFile ~/.ssh/$1"
