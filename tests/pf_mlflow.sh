#!/usr/bin/env bash
set -euo pipefail

kubectl port-forward -n mlflow svc/mlflow-service 5000:5000 &
PIPELINES_PID=$!

echo "Started mlflow port-forward, pid: $PIPELINES_PID"
echo PIPELINES_PID=$PIPELINES_PID >> pids.env

sleep 1

curl localhost:5000