import logging
import os

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
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
GLOBAL_NAMESPACE = os.getenv("namespace", "staging")
MLFLOW_STAGE = os.getenv("stage", "Staging")
backend = os.getenv("backend", "")
ML_SERVER = os.getenv("ML_SERVER", "kserve")



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
        self.managed_label = "mdc-direct"


    def __str__(self):
        return self.__class__.__name__

    def deploy_controller(self):
        """
        Manages the deployments from Mlflow
        """
        mlflowcontroller = MLflowMetadata(tracking_uri=TRACKING_URI, stage=MLFLOW_STAGE)
        logger.info(f"Mlflow tracking uri {TRACKING_URI}")
        logger.info(f"Mlflow Stage {MLFLOW_STAGE}")
        logger.info(f"backende {backend}")
        mlflow_models_metadata, read_deploy_yaml = mlflowcontroller.get_model_metadata(
            check_deploy=True,
            backend=backend,
            manager_label=self.managed_label,
            mlflow_deploy_config="deploy.yaml",
        )
        if len(mlflow_models_metadata.keys()) > 0:
            if ML_SERVER == "seldon":
                seldon.sync(
                    read_deploy_yaml,
                    mlflow_models_metadata,
                    MLFLOW_STAGE,
                    GLOBAL_NAMESPACE,
                    f"{self.managed_label}-mlflow-{backend}-seldon",
                    "mlflow",
                    backend,
                )
            elif ML_SERVER == "kserve":
                kserve.sync(read_deploy_yaml,
                            mlflow_models_metadata,
                            MLFLOW_STAGE,
                            GLOBAL_NAMESPACE,
                            f"{self.managed_label}-mlflow-{backend}-kserve",
                            "mlflow",
                            backend,
                            )

