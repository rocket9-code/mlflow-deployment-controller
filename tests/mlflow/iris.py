import os
import sys

import mlflow
import mlflow.sklearn
import pandas as pd
from minio import Minio
from mlflow.tracking import MlflowClient
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

try:
    client = Minio(
        "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
    )

    # Create bucket.
    client.make_bucket("artifacts")
except Exception as e:
    print(e)


def main(version, stage, MODEL_NAME):

    iris = datasets.load_iris()
    iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = iris.target
    iris_df["target"] = y

    train_df, test_df = train_test_split(
        iris_df, test_size=0.3, random_state=42, stratify=iris_df["target"]
    )
    X_train = train_df[
        [
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)",
        ]
    ]
    y_train = train_df["target"]

    X_test = test_df[
        [
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)",
        ]
    ]
    y_test = test_df["target"]

    EXPERIMENT_NAME = MODEL_NAME

    # print("IRIS train df shape")
    # print(X_train.shape)
    # print(y_train.shape)

    # print("IRIS test df shape")
    # print(X_test.shape)
    # print(y_test.shape)

    mlflow_client = MlflowClient()

    # Create an MLFlow experiment, if not already exists
    experiment_details = mlflow_client.get_experiment_by_name(EXPERIMENT_NAME)

    if experiment_details is not None:
        experiment_id = experiment_details.experiment_id
    else:
        experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)

    # Start an MLFlow experiment run
    with mlflow.start_run(
        experiment_id=experiment_id, run_name="iris dataset rf run"
    ) as run:
        # Log parameters

        mlflow.log_param("max_depth", 10)
        mlflow.log_param("random_state", 0)
        mlflow.log_param("n_estimators", 100)
        clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=0)
        clf.fit(X_train, y_train)
        iris_predict_y = clf.predict(X_test)

        roc_auc_score_val = roc_auc_score(
            y_test, clf.predict_proba(X_test), multi_class="ovr"
        )
        mlflow.log_metric("test roc_auc_score", roc_auc_score_val)

        # Log model
        result = mlflow.sklearn.log_model(clf, artifact_path="model")

        # Register a new version
    result = mlflow.register_model(result.model_uri, MODEL_NAME)

    mlflow_client.transition_model_version_stage(
        name=MODEL_NAME, version=version, stage=stage
    )
    registered_models = mlflow_client.list_registered_models()
    print(registered_models)


if __name__ == "__main__":
    for i in range(5):
        print(f"iris demo{i}")
        version = sys.argv[1]
        stage = sys.argv[2]
        main(MODEL_NAME=f"iris demo{i}", version=version, stage=stage)
