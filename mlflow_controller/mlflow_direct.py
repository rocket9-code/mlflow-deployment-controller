import logging
import os

from kubernetes import client as KubeClient
from kubernetes import config
from mlflow.tracking import MlflowClient

import mlflow_controller.storage
from mlflow_controller.seldon import sync

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
GLOBAL_NAMESPACE = os.getenv("namespace", "staging")
MLFLOW_STAGE = os.getenv("stage", "Staging")
os.environ[
    "AZURE_STORAGE_CONNECTION_STRING"
] = "DefaultEndpointsProtocol=https;AccountName=mlflowwianai;AccountKey=0ybOEesyxQzrqM5JXFba1obnYCAtotulPtXg8HRElutmVDoo/ExxZyXuVmu/DxxoA+5ajzD7iRK7+AStLHNtyA==;EndpointSuffix=core.windows.net"
os.environ[
    "AZURE_STORAGE_ACCESS_KEY"
] = "0ybOEesyxQzrqM5JXFba1obnYCAtotulPtXg8HRElutmVDoo/ExxZyXuVmu/DxxoA+5ajzD7iRK7+AStLHNtyA=="


class DeployConroller:
    """
    A class to Matain the controller

    ...

    Methods
    -------
    deploy_controller():
        Manages the deployments from Mlflow
    """

    def __init__(self):
        self.mlflow_client = MlflowClient(tracking_uri=TRACKING_URI)
        logger.info("Mlflow client initialized")
        self.object_init = mlflow_controller.storage.Artifact()
        try:
            config.load_kube_config()
        except config.ConfigException:
            config.load_incluster_config()
        self.kube_client = KubeClient.CustomObjectsApi()
        logger.info("KubeClient initialized")
        self.mlflow_deploy_config = "deploy.yaml"
        # self.stage = os.environ["stage"]
        self.model_details = []
        # self.Namespace = os.environ["namespace"]
        self.cloud = os.environ["cloud"]
        self.label = "app.kubernetes.io/managed-by=mdc-mlflow"

    def __str__(self):
        return self.__class__.__name__

    def deploy_controller(self):
        """
        Manages the deployments from Mlflow
        """
        mlflow_models_metadata = {}
        read_deploy_yaml = []
        registered_models = self.mlflow_client.list_registered_models()

        for registered_model in registered_models:
            for version in registered_model.latest_versions:
                if version.current_stage == MLFLOW_STAGE:
                    model_details = dict(version)
                    model_run_id = model_details["run_id"]
                    run_details = dict(self.mlflow_client.get_run(model_run_id).info)
                    name = model_details["name"]
                    artifact_uri = run_details["artifact_uri"]
                    mlflow_models_metadata[name] = {
                        "name": name,
                        "run_id": model_details["run_id"],
                        "source": model_details["source"],
                        "status": model_details["status"],
                        "version": model_details["version"],
                        "artifact_uri": artifact_uri,
                    }
                    logger.info(artifact_uri)
                    for file in self.mlflow_client.list_artifacts(model_run_id):
                        if file.path == self.mlflow_deploy_config:
                            if self.cloud == "gcp":
                                deploy_yaml = self.object_init.gcp_bucket(artifact_uri)
                            elif self.cloud == "azure_blob":
                                deploy_yaml = self.object_init.azure_blob(artifact_uri)
                            elif self.cloud == "aws_s3":
                                deploy_yaml = self.object_init.azure_blob(artifact_uri)

                            else:
                                raise ("unsupported Object Storage")
                        deploy_yaml["spec"]["predictors"][0]["graph"]["modelUri"] = name
                        deploy_yaml["spec"]["predictors"][0]["annotations"][
                            "predictor_version"
                        ] = model_details["version"]
                        try:
                            deploy_yaml["metadata"]["annotations"]
                        except:
                            deploy_yaml["metadata"]["annotations"] = {}
                        deploy_yaml["metadata"]["labels"][
                            "app.kubernetes.io/managed-by"
                        ] = "mdc-mlflow-direct"
                        read_deploy_yaml.append(deploy_yaml)
        logger.info(mlflow_models_metadata)
        if len(mlflow_models_metadata.keys()) > 0:
            sync(
                read_deploy_yaml,
                mlflow_models_metadata,
                MLFLOW_STAGE,
                GLOBAL_NAMESPACE,
                "mdc-mlflow-direct",
            )
