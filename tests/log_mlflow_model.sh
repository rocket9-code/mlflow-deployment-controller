#!/bin/bash
set -e
echo "Installing Mlflow ..."
pip install mlflow==1.25.1
pip install protobuf==3.20.*
pip install scikit-learn==0.23.2
pip install pandas==0.23.4
pip install boto3==1.22.9
pip install minio
pip install kubernetes
export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export MLFLOW_TRACKING_URI=http://localhost:5000
python ./tests/mlflow/iris.py 1 staging

