"""
__author__ = "Raghul Krishna"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__maintainer__ = "raghul Krishna"
__email__ = "rrkraghulkrishna@gmail.com"

"""
import logging
import os

import yaml
from google.cloud.storage import Client as GoogleClient
from kubernetes import client as KubeClient
from kubernetes import config
from mlflow.tracking import MlflowClient

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

# os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:57065"


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
        self.mlflow_client = MlflowClient()
        logger.info("Mlflow client initialized")
        self.google_client = GoogleClient()
        logger.info("Google client initialized")
        try:
            config.load_kube_config()
        except config.ConfigException:
            config.load_incluster_config()
        self.kube_client = KubeClient.CustomObjectsApi()
        logger.info("KubeClient initialized")
        self.mlflow_deploy_config = "deploy.yaml"
        self.stage = os.environ["stage"]
        self.model_details = []
        self.Namespace = "default"

    def __str__(self):
        return self.__class__.__name__

    def state_manager(self):
        """To delete resources deleted in Mlflow"""
        manifests = self.kube_client.list_cluster_custom_object(
            group="machinelearning.seldon.io",
            version="v1",
            plural="seldondeployments",
            label_selector="app.kubernetes.io/managed-by=mlflow-seldon",
        )
        for manifest in manifests["items"]:
            model_names = self.model_details
            manifest_name = manifest["metadata"]["name"]
            manifest_namespace = manifest["metadata"]["namespace"]
            print(model_names, manifest_name, manifest_namespace)
            model = next(
                (
                    item
                    for item in model_names
                    if item["deploy_name"] == manifest_name
                    and item["Namespace"] == manifest_namespace
                ),
                None,
            )
            if model:
                logger.info(
                    "Model %s Namespace %s in Sync ",
                    manifest["metadata"]["name"],
                    manifest["metadata"]["namespace"],
                )
            else:
                logger.info(
                    "Deleting a Deployment %s Namespace %s",
                    manifest["metadata"]["name"],
                    manifest["metadata"]["namespace"],
                )
                self.kube_client.delete_namespaced_custom_object(
                    group="machinelearning.seldon.io",
                    version="v1",
                    plural="seldondeployments",
                    name=manifest["metadata"]["name"],
                    namespace=manifest["metadata"]["namespace"],
                )
        self.model_details = []

    def deploy_controller(self):
        """
        Manages the deployments from Mlflow
        """
        model_versions = []
        for registered_model in self.mlflow_client.list_registered_models():
            for version in registered_model.latest_versions:
                model_versions.append(version)
        for version in model_versions:
            if version.current_stage == self.stage:
                print(version.current_stage)
                for file in self.mlflow_client.list_artifacts(version.run_id):
                    if file.path == self.mlflow_deploy_config:
                        model_name = version.name.lower()
                        model_run_id = version.run_id
                        model_source = version.source
                        run_details = self.mlflow_client.get_run(version.run_id)
                        artifact_uri = run_details.info.artifact_uri
                        bucket = artifact_uri.split("/")[2]
                        object_name = (
                            "/".join(artifact_uri.split("/")[3:])
                            + f"/{self.mlflow_deploy_config}"
                        )
                        bucket = self.google_client.get_bucket(bucket)
                        blob = bucket.get_blob(object_name)
                        downloaded_file = blob.download_as_text(encoding="utf-8")
                        deploy_yaml = yaml.safe_load(downloaded_file)
                        logger.info(
                            "Model Name: %s, Model Run Id: %s",
                            model_name,
                            model_run_id,
                        )
                        self.model_details.append(
                            {
                                "name": model_name,
                                "deploy_name": deploy_yaml["metadata"]["name"],
                                "Namespace": self.Namespace,
                            }
                        )
                        try:
                            self.kube_client.create_namespaced_custom_object(
                                group="machinelearning.seldon.io",
                                version="v1",
                                plural="seldondeployments",
                                body=deploy_yaml,
                                namespace=self.Namespace,
                            )
                            logger.info(
                                "Created a Deployment %s Namespace %s",
                                model_name,
                                self.Namespace,
                            )
                        except KubeClient.rest.ApiException:
                            self.kube_client.patch_namespaced_custom_object(
                                group="machinelearning.seldon.io",
                                version="v1",
                                plural="seldondeployments",
                                body=deploy_yaml,
                                name=deploy_yaml["metadata"]["name"],
                                namespace=self.Namespace,
                            )
                            logger.info(
                                "Patched a Deployment %s  Namespace %s",
                                model_name,
                                self.Namespace,
                            )
        self.state_manager()
