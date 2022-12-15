#!/bin/bash
set -e
echo "Installing Deployment Controller ..."

helm install mlflow-controller charts/mlflow-controller  --set image.tag=$GITHUB_SHA -n mlflow
kubectl get deployment -n mlflow
kubectl get cm -n mlflow
kubectl get po -n mlflow
kubectl create secret generic github-secret --from-literal=githubtoken=testpw
echo "Waiting for Deployment Controller to be ready ..."
# kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (mlflow-controller)' --timeout=180s -n mlflow
sleep 180
kubectl logs deployment/mlflow-controller -n mlflow