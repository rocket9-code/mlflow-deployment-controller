#!/bin/bash
set -e
echo "Installing Mlflow ..."
helm repo add minio https://charts.bitnami.com/bitnami
helm install minio minio/minio -n mlflow
kubectl wait --for=condition=ready pod -l 'app in (minio)' --timeout=180s -n mlflow