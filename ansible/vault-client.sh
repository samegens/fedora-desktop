#!/bin/bash
set -euo pipefail

# Check environment variable first
if [ -n "${ANSIBLE_VAULT_PASSWORD:-}" ]; then
    echo "$ANSIBLE_VAULT_PASSWORD"
    exit 0
fi

# Check file next
if [ -f ~/.vault_pass ]; then
    cat ~/.vault_pass
    exit 0
fi

# Check Dropbox file
if [ -f ~/Dropbox/ansible/.vault_pass ]; then
    cat ~/Dropbox/ansible/.vault_pass
    exit 0
fi

# Check if az CLI is available
if ! command -v az &> /dev/null; then
    echo "Error: ANSIBLE_VAULT_PASSWORD not set, ~/.vault_pass not found, and 'az' CLI not installed" >&2
    exit 1
fi

# Finally, try Azure Key Vault
az account show > /dev/null
JSON=$(az keyvault secret show --id https://blauwelucht-secrets-kv.vault.azure.net/secrets/ansible-vault-password --query value)
PASSWORD=$(echo "$JSON" | tr -d '"')
echo "$PASSWORD"

