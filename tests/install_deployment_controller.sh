#!/bin/bash
set -e
echo "Installing Deployment Controller ..."
kubectl create ns staging
helm install mlflow-controller charts/mlflow-controller  --set image.tag=$GITHUB_SHA -n mlflow --set mlflow.backend==s3
kubectl get deployment -n mlflow
kubectl get cm -n mlflow
kubectl get po -n mlflow
kubectl create secret generic github-secret --from-literal=githubtoken=testpw
echo "Waiting for Deployment Controller to be ready ..."
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/name=mlflow-controller" -o jsonpath="{.items[0].metadata.name}")

kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (mlflow-controller)' --timeout=180s -n mlflow
kubectl describe po $POD_NAME -n mlflow
sleep 180
kubectl logs deployment/mlflow-controller -n mlflow
kubectl get seldondeployment --all-namespaces
kubectl get seldondeployment mlflow-var   -n staging -o yaml