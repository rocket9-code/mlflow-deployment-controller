#!/bin/bash
set -e
echo "Installing Seldon Core ..."
kubectl create namespace seldon-system
helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set istio.enabled=true \
    --namespace seldon-system
echo "Waiting for Seldon Core to be ready ..."
kubectl wait --for=condition=ready pod -l 'app in (seldon)' --timeout=180s -n seldon-system