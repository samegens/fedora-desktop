#!/bin/bash
set -eo pipefail
set -u

cd "$(dirname "$0")"

cinc-auditor exec inspec/fedora-desktop --chef-license=accept-silent --auto-install-gems
