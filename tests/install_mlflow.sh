#!/bin/bash
set -e
echo "Installing Mlflow ..."
kubectl create ns mlflow
helm repo add minio https://charts.bitnami.com/bitnami
helm install minio minio/minio -n mlflow
kubectl get po -n mlflow
kubectl get sc
kubectl get pvc -n mlflow
kubectl describe pvc minio -n mlflow
kubectl get  pv -n mlflow
export ROOT_USER=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-user}" | base64 -d)
export ROOT_PASSWORD=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-password}" | base64 -d)
echo $ROOT_USER
echo $ROOT_PASSWORD
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (minio)' --timeout=180s -n mlflow