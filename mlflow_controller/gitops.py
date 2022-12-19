import glob
import logging
import os
import shutil
import uuid

import yaml
from git import Repo
from kubernetes import config

from mlflow_controller.mlservers import seldon
from mlflow_controller.mlservers import kserve
from mlflow_controller.registries.mlflow import MLflowMetadata

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

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:9000")
GIT_USER = os.getenv("GIT_USER", "")
GIT_PASSWORD = os.getenv("GIT_PASSWORD", "")
GIT_REPO = os.getenv("GIT_REPO", "github.com/rocket9-code/model-deployments")
if GIT_PASSWORD:
    GIT_URL = f"https://{GIT_USER}:{GIT_PASSWORD}@{GIT_REPO}"
else:
    GIT_URL = f"https://{GIT_REPO}"

MANIFEST_LOCATION = os.getenv("MANIFEST_LOCATION", "staging")
GLOBAL_NAMESPACE = os.getenv("namespace", "staging")
MLFLOW_STAGE = os.getenv("stage", "Staging")
backend = os.getenv("backend", "")
BRANCH = os.getenv("BRANCH", "main")
ML_SERVER = os.getenv("ML_SERVER", "kserve")



class GitopsMDC:
    def gitops_mlflow_controller(self):

        folder_name = str(uuid.uuid4())
        path = "./tmp/" + folder_name
        if not os.path.exists(path):
            os.makedirs(path)
        logger.info(f"Cloning repo {GIT_URL} with branch {BRANCH}")
        Repo.clone_from(GIT_URL, path, single_branch=True, branch=BRANCH)
        try:
            config.load_kube_config()
        except config.ConfigException:
            config.load_incluster_config()
        manifest_path = path + "/" + MANIFEST_LOCATION
        deploy_yamls = glob.glob(f"{manifest_path}/*.yaml") + glob.glob(
            f"{manifest_path}/*.yml"
        )
        mlflowcontroller = MLflowMetadata(tracking_uri=TRACKING_URI, stage=MLFLOW_STAGE)
        logger.info(f"Mlflow tracking uri {TRACKING_URI}")
        logger.info(f"Mlflow Stage {MLFLOW_STAGE}")
        logger.info(f"backend {backend}")
        mlflow_models_metadata, _ = mlflowcontroller.get_model_metadata(
            check_deploy=False, backend=backend
        )
        read_seldon_deploy_yamls = []
        for i in deploy_yamls:
            with open(i, "r") as stream:
                try:
                    deploy_yaml = yaml.safe_load(stream)
                    resource_group = deploy_yaml["apiVersion"].split("/")[0]
                    if ML_SERVER == "seldon":
                        if resource_group == "machinelearning.seldon.io":
                            read_seldon_deploy_yamls.append(deploy_yaml)
                    elif ML_SERVER == "kserve":
                        if resource_group == "serving.kserve.io":
                            read_seldon_deploy_yamls.append(deploy_yaml)
                except yaml.YAMLError as exc:
                    logger.error(exc)
        if len(mlflow_models_metadata.keys()) > 0:
            if ML_SERVER == "seldon":
                seldon.sync(
                    read_seldon_deploy_yamls,
                    mlflow_models_metadata,
                    MLFLOW_STAGE,
                    GLOBAL_NAMESPACE,
                    f"mdc-gitops-{backend}-mlflow-seldon",
                    "mlflow",
                    backend
                )
            elif ML_SERVER == "kserve":
                kserve.sync(
                    read_seldon_deploy_yamls,
                    mlflow_models_metadata,
                    MLFLOW_STAGE,
                    GLOBAL_NAMESPACE,
                    f"mdc-gitops-{backend}-mlflow-kserve",
                    "mlflow",
        shutil.rmtree(path, ignore_errors=True)
