# Ubuntu Desktop Configuration

[![CI](https://github.com/samegens/ubuntu-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/samegens/ubuntu-desktop/actions/workflows/ci.yml)
[![Secret Detection](https://github.com/samegens/ubuntu-desktop/actions/workflows/secrets-detection.yml/badge.svg)](https://github.com/samegens/ubuntu-desktop/actions/workflows/secrets-detection.yml)

Ansible playbook to automate my Ubuntu desktop setup and configuration.

## Features

- using [`vault-client.sh`](ansible/vault-client.sh) to retrieve the Ansible vault password
- [wrapper script](ansible/_run.sh) that creates a separate log file for each run
- same wrapper script summarizes the result of an ansible-playbook run (see [`summarize_log`](ansible/summarize_log))
- lots of ways to configure desktop stuff (see [`playbook.yml`](ansible/playbook.yml) and [`tasks`](ansible/tasks/))
- [git commit hooks](.githooks) and [Github workflow](.github/workflows/secrets-detection.yml) to prevent plaintext secrets from ending up in Git

## Setup

1. Clone the repository
2. Run [`./setup-repo.sh`](setup-repo.sh) to enable git hooks
3. Configure your secrets, see [`ansible/vault-client.sh`](ansible/vault-client.sh) for multiple ways to configure the Ansible vault password
4. Run the playbook: `cd ansible; ./run-local.sh <extra ansible-playbook arguments>` (see [`run-local.sh`](ansible/run-local.sh))

## Secret Detection

This repository uses multiple tools to prevent secret leaks:

- **Gitleaks**: Pattern-based detection
- **TruffleHog**: Entropy-based detection
- **detect-secrets**: Context-aware detection

The pre-commit hook automatically scans for secrets before commits.
