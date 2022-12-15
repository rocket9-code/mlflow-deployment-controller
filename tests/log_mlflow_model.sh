#!/bin/bash
set -e
echo "Installing Mlflow ..."
pip install mlflow==1.25.1
pip install protobuf==3.20.*
pip install scikit-learn==0.23.2
pip install pandas==0.23.4
export MLFLOW_TRACKING_URI=http://localhost:5000
python ./tests/mlflow/iris.py