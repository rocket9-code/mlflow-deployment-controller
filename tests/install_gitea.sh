#!/usr/bin/env bash
set -euo pipefail

helm repo add gitea-charts https://dl.gitea.io/charts/
helm install gitea gitea-charts/gitea --set "gitea.admin.username=mdcadmin" --set "gitea.admin.password=password" --set "gitea.admin.email=mdcadmin@local.domain"
kubectl wait --for=condition=ready pod -l 'app.kubernetes.io/name in (gitea)' --timeout=180s

kubectl --namespace default port-forward svc/gitea-http 3000:3000 &
GITEA_PID=$!
