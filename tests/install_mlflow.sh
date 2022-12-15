#!/bin/bash
set -e
echo "Installing Mlflow ..."
kubectl create ns mlflow
helm repo add minio https://charts.bitnami.com/bitnami
helm install minio minio/minio -n mlflow --set auth.rootUser=admin --set auth.rootPassword=admin

export ROOT_USER=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-user}" | base64 -d)
export ROOT_PASSWORD=$(kubectl get secret --namespace mlflow minio -o jsonpath="{.data.root-password}" | base64 -d)

kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (minio)' --timeout=380s -n mlflow
kubectl apply -f tests/mlflow-cm.yaml -n mlflow
helm repo add rocket9-code https://rocket9-code.github.io/hello-mlflow/
helm install mlflow rocket9-code/mlflow  -n mlflow --set artifact.ArtifactRoot=s3://artifacts  --set envFromconfigMap=minio-cm
kubectl get po -n mlflow
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/name=mlflow,app.kubernetes.io/instance=mlflow" -o jsonpath="{.items[0].metadata.name}")
kubectl describe po $POD_NAME -n mlflow
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (mlflow)' --timeout=380s -n mlflow
