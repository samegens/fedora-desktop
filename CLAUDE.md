# fedora-desktop

Ansible playbook that automates Sebastiaan's Fedora KDE desktop setup and configuration. Single source of truth for how his machines are provisioned and kept configured.

## Secrets model (important)

This repo assumes a **sibling directory** `../fedora-desktop-secrets` containing the actual secrets (vault-encrypted vars, SSH private keys, service account JSON, etc.). Everything under this repo that looks like a secret (`ansible/group_vars/all/vault.yml`, `ansible/host_vars/*/vault.yml`, `ansible/files/<host>/ssh/<host>`, etc.) is actually a **symlink** into that sibling directory, created by `setup-repo.sh`.

- Never assume a vault/key file's content — check whether it's a symlink (`ls -l`) and remember the real content lives outside this repo, typically synced via Dropbox.
- `*.example` files (e.g. `vault.yml.example`) show the expected structure for new setups.
- `.githooks` + secret-scanning CI (Gitleaks, TruffleHog, detect-secrets) exist specifically to stop plaintext secrets leaking into this repo — don't bypass or weaken them.
- Vault password resolution order is in `ansible/vault-client.sh`: `$ANSIBLE_VAULT_PASSWORD` env var → `~/.vault_pass` → `~/Dropbox/ansible/.vault_pass` → Azure Key Vault (`az keyvault secret show ... ansible-vault-password`).

## Two run modes: local vs remote

The same playbook (`ansible/playbook.yml`) targets either:
- **`localhost`** — reconfigure the machine you're currently on. Run via `cd ansible && ./run-local.sh <extra args>`.
- **`remote`** — bootstrap a brand-new/different machine from the current one over SSH. Run via `cd ansible && ./run.sh <host> <extra args>`.

Both go through `ansible/_run.sh`, which sets a timestamped log file under `/var/log/ansible`, runs `ansible-playbook --diff --limit <server>`, and pipes the result through `ansible/summarize_log/summarize_log.py` for a human-readable summary.

## Inventory hosts (`ansible/inventory`)

- `localhost` — the current machine.
- `raaf` — a specific physical box: an old machine upgraded from Ubuntu to be a gaming machine.
- `remote` — not a fixed machine; a generic placeholder host used whenever configuring *some* new/different desktop machine from the current one.

## Layout

- `ansible/playbook.yml` — the main play; imports one task file per feature/tool from `ansible/tasks/*.yml` (KDE/Gnome, Docker, Dropbox, VirtualBox, k3s, NVIDIA, VS Code, dotfiles, dev toolchains like Go/Rust/Node, etc.).
- `ansible/group_vars/all/vars.yml` — shared vars (username, package lists, tool versions, static host-entries).
- `ansible/host_vars/<host>/vars.yml` — per-host overrides.
- `ansible/files/` — static files pushed to machines, including per-host SSH key directories and Terraform/RPA secrets (symlinked, see above).
- `ansible/summarize_log/` — small Python package (with unit tests) that turns an ansible-playbook log into a readable run summary.
- `inspec/fedora-desktop/` — Inspec/Cinc Auditor controls (`controls/system.rb`, `controls/tools.rb`) that verify the playbook actually configured the machine correctly. Run locally with `./test-local.sh` (uses `cinc-auditor`, not `inspec`, due to a past inspec/docker_container bug workaround — see commit `564ed4e`).
- `setup-repo.sh` — one-time repo bootstrap: points git at `.githooks` and symlinks in the secrets from `../fedora-desktop-secrets`.
- `prepare.sh` — bootstraps Ansible itself on a fresh box before the playbook can run (installs pip + ansible; expects `/root/.vault_pass`).

## CI (`.github/workflows/ci.yml`)

Three independent jobs: `ansible-lint` (config in `ansible/.ansible-lint`), `pyright` type-check on `ansible/summarize_log/`, and Python `unittest` for `ansible/summarize_log/tests`. A separate workflow (`secrets-detection.yml`) scans pushes for leaked secrets.

## Conventions

- All Ansible `register:` variables must use the `_result` suffix, e.g. `k3s_stat_result`, `passlib_check_result` — never bare `k3s_stat`.
- Tasks are tagged consistently (e.g. `dnf`, `flatpak`, `dirs`) and imported via `import_tasks`, not inlined in `playbook.yml` — new features should follow the same one-task-file-per-feature pattern.
