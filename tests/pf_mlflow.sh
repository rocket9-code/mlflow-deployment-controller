#!/usr/bin/env bash
set -euo pipefail

kubectl port-forward -n mlflow svc/mlflow-service 5000:5000 &
MLFLOW_PID=$!

echo "Started mlflow port-forward, pid: $MLFLOW_PID"
echo MLFLOW_PID=$MLFLOW_PID >> pids.env

sleep 1


kubectl port-forward --namespace mlflow svc/minio 9000:9000 &
MINIO_PID=$!

echo "Started mlflow port-forward, pid: $MINIO_PID"
echo MINIO_PID=$MINIO_PID >> pids.env

sleep 1

curl -X POST http://localhost:5000/api/2.0/preview/mlflow/experiments/create -d '{"name":"test"}'