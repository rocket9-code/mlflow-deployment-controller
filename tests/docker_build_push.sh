#!/bin/bash
set -e
echo "Installing build test image and push ..."
docker build -t hellomlops/mlflow-deployment-controller:$TAG .
docker push hellomlops/mlflow-deployment-controller:$TAG
