#!/bin/bash
set -e
echo "Installing Mlflow ..."
kubectl create ns mlflow
helm repo add minio https://charts.bitnami.com/bitnami
helm install minio minio/minio -n mlflow
helm repo add hello-mlflow https://rocket9-code.github.io/hello-mlflow/
helm install hello-mlflow hello-mlflow/hello-mlflow

export ROOT_USER=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-user}" | base64 -d)
export ROOT_PASSWORD=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-password}" | base64 -d)
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (minio)' --timeout=180s -n mlflow