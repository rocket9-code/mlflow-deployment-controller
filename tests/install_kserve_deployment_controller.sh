#!/bin/bash
set -e
echo "Installing Kserve Deployment Controller ..."
kubectl create ns staging
kubectl create ns production
kubectl create secret generic github-secret -n mlflow --from-literal=githubtoken=password

helm install mdc-staging charts/mlflow-controller  --set image.tag=$GITHUB_SHA  --set image.pullPolicy=Never --set image.repository=docker.io/hellomlops/mlflow-deployment-controller -n mlflow --set mlflow.backend=s3 --set gitops.deploymentLocation=staging/ --set mlserver=kserve 
helm install mdc-production charts/mlflow-controller  --set image.tag=$GITHUB_SHA  --set image.pullPolicy=Never --set image.repository=docker.io/hellomlops/mlflow-deployment-controller -n mlflow --set mlflow.stage=Production --set mlflow.namespace=production --set mlflow.backend=s3 --set gitops.deploymentLocation=staging/ --set mlserver=kserve

kubectl get deployment -n mlflow
kubectl get cm -n mlflow
kubectl get po -n mlflow
echo "Waiting for Deployment Controller to be ready ..."
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/instance=mdc-staging" -o jsonpath="{.items[0].metadata.name}")

kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/instance in (mdc-staging)' --timeout=180s -n mlflow
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/instance=mdc-production" -o jsonpath="{.items[0].metadata.name}")

kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/instance in (mdc-production)' --timeout=180s -n mlflow


kubectl describe po $POD_NAME -n mlflow
sleep 180
kubectl logs deployment/mlflow-controller -n mlflow
kubectl get inferenceservice --all-namespaces
kubectl get inferenceservice sklearn-iris-minio  -n staging -o yaml

export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export MLFLOW_TRACKING_URI=http://localhost:5000
python ./tests/mlflow/list_model.py $mlserver