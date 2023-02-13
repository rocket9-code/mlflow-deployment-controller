#!/bin/bash
set -e
echo "Installing build test image and push ..."
docker build -t tachyongroup/mdc-test:$GITHUB_SHA .
# docker push tachyongroup/mdc-test:$GITHUB_SHA
kind load docker-image tachyongroup/mdc-test:$GITHUB_SHA
