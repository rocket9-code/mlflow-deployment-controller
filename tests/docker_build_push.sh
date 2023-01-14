#!/bin/bash
set -e
echo "Installing build test image and push ..."
docker build -t hellomlops/mlflow-deployment-controller:$GITHUB_SHA .
# docker push hellomlops/mlflow-deployment-controller:$GITHUB_SHA
kind load docker-image hellomlops/mlflow-deployment-controller:$GITHUB_SHA
