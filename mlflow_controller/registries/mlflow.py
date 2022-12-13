import logging
import os

from mlflow.tracking import MlflowClient

from mlflow_controller.registries import mlflow_backend

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


class MLflowMetadata:
    def __init__(self, tracking_uri, stage):
        self.mlflow_client = MlflowClient(tracking_uri=tracking_uri)
        logger.info("Mlflow client initialized")
        self.object_init = mlflow_backend.Artifact()
        self.stage = stage

    def __str__(self):
        return self.__class__.__name__

    def get_model_metadata(
        self,
        check_deploy=False,
        manager_label="mdc-mlflow-direct",
        backend="",
        mlflow_deploy_config="deploy.yaml",
    ):
        mlflow_models_metadata = {}
        read_deploy_yaml = []
        registered_models = self.mlflow_client.list_registered_models()
        for registered_model in registered_models:
            for version in registered_model.latest_versions:
                if version.current_stage == self.stage:
                    model_details = dict(version)
                    model_run_id = model_details["run_id"]
                    run_details = dict(self.mlflow_client.get_run(model_run_id).info)
                    name = model_details["name"]
                    model_template = f'mlflow.{backend}["{name}"]'
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
                    if check_deploy:
                        for file in self.mlflow_client.list_artifacts(model_run_id):
                            if file.path == mlflow_deploy_config:
                                if backend == "gcs":
                                    deploy_yaml = self.object_init.gcp_bucket(
                                        artifact_uri
                                    )
                                elif backend == "blob":
                                    deploy_yaml = self.object_init.azure_blob(
                                        artifact_uri
                                    )
                                elif backend == "s3":
                                    deploy_yaml = self.object_init.aws_s3(artifact_uri)
                                else:
                                    raise ("unsupported Object Storage")
                            deploy_yaml["spec"]["predictors"][0]["graph"][
                                "modelUri"
                            ] = model_template
                            deploy_yaml["spec"]["predictors"][0]["annotations"][
                                "predictor_version"
                            ] = model_details["version"]
                            try:
                                deploy_yaml["metadata"]["annotations"]
                            except:
                                deploy_yaml["metadata"]["annotations"] = {}
                            deploy_yaml["metadata"]["labels"][
                                "app.kubernetes.io/mdc-type"
                            ] = manager_label
                            read_deploy_yaml.append(deploy_yaml)
        ml_metadata = {"mlflow": {f"{backend}": mlflow_models_metadata}}
        return ml_metadata, read_deploy_yaml
