#!/bin/bash
set -e
echo "Installing Kserve ..."
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.9/hack/quick_install.sh" | bash
