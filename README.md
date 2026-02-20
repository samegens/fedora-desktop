# Fedora Desktop Configuration

[![CI](https://github.com/samegens/fedora-desktop/actions/workflows/ci.yml/badge.svg)](https://github.com/samegens/fedora-desktop/actions/workflows/ci.yml)
[![Secret Detection](https://github.com/samegens/fedora-desktop/actions/workflows/secrets-detection.yml/badge.svg)](https://github.com/samegens/fedora-desktop/actions/workflows/secrets-detection.yml)

Ansible playbook to automate my Fedora KDE desktop setup and configuration.

## Features

- using [`vault-client.sh`](ansible/vault-client.sh) to retrieve the Ansible vault password
- [wrapper script](ansible/_run.sh) that creates a separate log file for each run
- same wrapper script summarizes the result of an ansible-playbook run (see [`summarize_log`](ansible/summarize_log))
- lots of ways to configure desktop stuff (see [`playbook.yml`](ansible/playbook.yml) and [`tasks`](ansible/tasks/))
- [Github workflow](.github/workflows/secrets-detection.yml) to prevent plaintext secrets from ending up in Git
- secrets (vault-encrypted vars, SSH keys) are kept in a sibling `fedora-desktop-secrets` directory and symlinked in by `setup-repo.sh`

## Setup

1. Clone the repository
2. Create the `fedora-desktop-secrets` directory next to this repo (see vault.yml.example files for the expected structure)
3. Run [`./setup-repo.sh`](setup-repo.sh) to create symlinks to secrets and enable git hooks
4. Configure your vault password, see [`ansible/vault-client.sh`](ansible/vault-client.sh)
5. Run the playbook:
   - Local: `cd ansible; ./run-local.sh <extra ansible-playbook arguments>`
   - Remote: `cd ansible; ./run.sh <host> <extra ansible-playbook arguments>`

## Secret Detection

This repository uses multiple tools to prevent secret leaks:

- **Gitleaks**: Pattern-based detection
- **TruffleHog**: Entropy-based detection
- **detect-secrets**: Context-aware detection

The [secrets detection workflow](.github/workflows/secrets-detection.yml) automatically scans for secrets on push.
