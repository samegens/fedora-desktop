#!/bin/bash
# Repository setup script
# Configures git hooks and creates symlinks to fedora-desktop-secrets

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_DIR="$(cd "$REPO_DIR/../fedora-desktop-secrets" 2>/dev/null && pwd)" || {
  echo "Error: fedora-desktop-secrets directory not found at $REPO_DIR/../fedora-desktop-secrets"
  echo "Make sure the secrets directory exists and Dropbox is synced before running this script."
  exit 1
}

echo "Setting up repository..."
echo "Secrets directory: $SECRETS_DIR"
echo ""

# Configure git to use .githooks directory
git -C "$REPO_DIR" config core.hooksPath .githooks
echo "✓ Configured git to use .githooks directory"

# Create symlinks to secrets
create_symlink() {
  local target="$1"
  local link="$2"
  if [ -L "$link" ]; then
    echo "  (already exists) $link"
  elif [ -e "$link" ]; then
    echo "  WARNING: $link exists and is not a symlink, skipping"
  else
    ln -s "$target" "$link"
    echo "  ✓ $link"
  fi
}

echo ""
echo "Creating symlinks to secrets..."

create_symlink "$SECRETS_DIR/ansible/group_vars/all/vault.yml" \
               "$REPO_DIR/ansible/group_vars/all/vault.yml"

create_symlink "$SECRETS_DIR/ansible/host_vars/localhost/vault.yml" \
               "$REPO_DIR/ansible/host_vars/localhost/vault.yml"

create_symlink "$SECRETS_DIR/ansible/host_vars/raaf/vault.yml" \
               "$REPO_DIR/ansible/host_vars/raaf/vault.yml"

create_symlink "$SECRETS_DIR/ansible/host_vars/remote/vault.yml" \
               "$REPO_DIR/ansible/host_vars/remote/vault.yml"

for key in bhosted cubi fitlet fitlet-tst fitlet-acc fitpc fitpc-tst \
           github_adopteerregenwoud github_blauwe-lucht github_samegens \
           gitlab liteserver liteserver-tst; do
  create_symlink "$SECRETS_DIR/ansible/files/$key/ssh/$key" \
                 "$REPO_DIR/ansible/files/$key/ssh/$key"
done

create_symlink "$SECRETS_DIR/ansible/files/terraform/secret-vars.tfvars.encrypted" \
               "$REPO_DIR/ansible/files/terraform/secret-vars.tfvars.encrypted"

create_symlink "$SECRETS_DIR/ansible/files/blauwe-lucht-rpa/blauwe-lucht-rpa-f89be6fb53f3.json" \
               "$REPO_DIR/ansible/files/blauwe-lucht-rpa/blauwe-lucht-rpa-f89be6fb53f3.json"

echo ""
echo "Repository setup complete!"
