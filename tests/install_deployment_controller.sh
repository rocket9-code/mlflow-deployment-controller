#!/bin/bash
set -e
echo "Installing Deployment Controller ..."

kubectl create ns mlflow
helm install mlflow-controller charts/mlflow-controller  --set image.tag=$GITHUB_SHA
kubectl get po -n mlflow
echo "Waiting for Deployment Controller to be ready ..."
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (mlflow-controller)' --timeout=180s -n mlflow