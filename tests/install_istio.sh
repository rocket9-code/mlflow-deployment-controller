#!/bin/bash
set -e
echo "Installing Istio service mesh ..."
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
kubectl create namespace istio-system
helm install istio-base istio/base -n istio-system
helm install istiod istio/istiod -n istio-system --wait
helm status istiod -n istio-system

echo "Waiting for Istio service mesh to be ready ..."
kubectl wait --for=condition=ready pod -l 'app in (istiod)' --timeout=180s -n  istio-system