#!/usr/bin/env bash
set -euo pipefail

kubectl port-forward -n mlflow svc/mlflow-service 5000:5000 &
PIPELINES_PID=$!

echo "Started mlflow port-forward, pid: $PIPELINES_PID"
echo PIPELINES_PID=$PIPELINES_PID >> pids.env

sleep 1

curl -X POST http://localhost:5000/api/2.0/preview/mlflow/experiments/create -d '{"name":"test"}'