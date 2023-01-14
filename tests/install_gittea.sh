#!/usr/bin/env bash
set -euo pipefail

helm repo add gitea-charts https://dl.gitea.io/charts/
helm install gitea gitea-charts/gitea --set "gitea.admin.username=mdcadmin" --set "gitea.admin.password=password" --set "gitea.admin.email=mdcadmin@local.domain"
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/instance in (gitea)' --timeout=180s

kubectl --namespace default port-forward svc/gitea-http 3000:3000 &
MLFLOW_PID=$!

curl -X 'POST' \
  'http://localhost:3000/api/v1/user/repos' \
  -H 'accept: application/json' \
  -H 'authorization: Basic bWRjYWRtaW46cGFzc3dvcmQ=' \
  -H 'Content-Type: application/json' \
  -d '{
  "auto_init": false,
  "default_branch": "main",
  "description": "demo",
  "name": "repo-test",
  "private": false,
  "template": false,
  "trust_model": "default"
}'

