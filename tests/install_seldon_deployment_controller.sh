#!/bin/bash
set -e
echo "Installing Seldon Deployment Controller ..."
kubectl create ns staging
kubectl create secret generic github-secret -n mlflow --from-literal=githubtoken=password

helm install mdc-staging charts/mlflow-controller  -n mlflow  --set image.tag=$GITHUB_SHA  --set image.pullPolicy=Never  --set image.repository=docker.io/tachyongroup/mdc-test --set mlflow.backend=s3 --set gitops.deploymentLocation=staging/ --set mlserver=seldon --set gitops.repository=gitea-http.default.svc.cluster.local:3000/mdcadmin/repo-test --set  gitops.protocol=http
kubectl apply -f tests/repo-test/staging/seldon-secret.yaml -n staging
kubectl get deployment -n mlflow
kubectl get cm -n mlflow
kubectl get po -n mlflow

echo "Waiting for Deployment Controller to be ready ..."
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/instance=mdc-staging" -o jsonpath="{.items[0].metadata.name}")
sleep 180
kubectl describe po $POD_NAME -n mlflow
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/instance in (mdc-staging)' --timeout=380s -n mlflow


kubectl describe po $POD_NAME -n mlflow
sleep 180
kubectl logs deployment/mdc-staging-mlflow-controller -n mlflow
kubectl get seldondeployment --all-namespaces
kubectl get seldondeployment mlflow-var-minio   -n staging -o yaml

export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export MLFLOW_TRACKING_URI=http://localhost:5000
python ./tests/mlflow/list_model.py $mlserver


python ./tests/mlflow/test_deploy.py