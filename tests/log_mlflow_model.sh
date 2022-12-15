#!/bin/bash
set -e
echo "Installing Mlflow ..."
pip install mlflow==1.25.1
pip install protobuf==3.20.*
export MLFLOW_TRACKING_URI=http://localhost:5000
python ./tests/mlflow/iris.py