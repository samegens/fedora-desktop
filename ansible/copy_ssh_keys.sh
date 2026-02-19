#!/bin/bash
set -ueo pipefail

mkdir -p files/$1/ssh

cp ~/.ssh/$1.pub files/$1/ssh
cp ~/.ssh/$1 /tmp
ansible-vault encrypt /tmp/$1
mv /tmp/$1 files/$1/ssh
