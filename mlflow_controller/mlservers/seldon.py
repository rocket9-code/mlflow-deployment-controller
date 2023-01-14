import json
import logging
import re

from kubernetes import client as KubeClient
from kubernetes import config

from mlflow_controller.mlservers.rclone import rclone_source
from mlflow_controller.utils.var_extract import var_parser
from mlflow_controller.mlservers.utils import update_modeluris, mlflow_model_search

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

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
kube_client = KubeClient.CustomObjectsApi()


class InvalidVariable(Exception):
    "Raised when wrong templates"
    pass


def sync(
    deploy_yamls,
    model_metadata,
    stage,
    GLOBAL_NAMESPACE,
    controller_label_value,
    registry_name,
    backend,
):
    git_models = []
    for deploy_yaml in deploy_yamls:
        resource_group = deploy_yaml["apiVersion"].split("/")[0]
        if resource_group == "machinelearning.seldon.io":
            models = list(
                set(mlflow_model_search("modelUri", deploy_yaml, search_result=[]))
            )
            logger.info(f"models {models}")
            rep_deploy_yaml = deploy_yaml
            try:
                rep_deploy_yaml["metadata"]["annotations"]

            except KeyError:
                rep_deploy_yaml["metadata"]["annotations"] = {}
            try:
                rep_deploy_yaml["metadata"]["labels"]

            except KeyError:
                rep_deploy_yaml["metadata"]["labels"] = {}
            deploy = False
            for m in models:
                try:
                    pattern = r"\{\{\s(.*)\s\}\}"
                    model_jinja = re.findall(pattern, m)[0]
                    model_name, bk_name, rg_name = var_parser(model_jinja)
                    if (bk_name != backend) or (rg_name != registry_name):
                        raise InvalidVariable
                    model = model_metadata[registry_name][backend][model_name]
                    run_id = model["run_id"]
                    rep_deploy_yaml = update_modeluris(
                        rep_deploy_yaml,
                        f'{{{{ {registry_name}.{backend}["{model_name}"] }}}}',
                        rclone_source(model["source"], backend),
                    )
                    rep_deploy_yaml["metadata"]["annotations"][
                        f"mdc/mlflow-{run_id}"
                    ] = str(model)
                    rep_deploy_yaml["metadata"]["annotations"][
                        "mdc/mlflow-stage"
                    ] = stage
                    rep_deploy_yaml["metadata"]["labels"][
                        "app.kubernetes.io/mdc-type"
                    ] = controller_label_value
                    rep_deploy_yaml["metadata"]["labels"][
                        "app.kubernetes.io/managed-by"
                    ] = "mdc"
                    deploy = True
                    name = rep_deploy_yaml["metadata"]["name"]
                except InvalidVariable:
                    deploy = False
                    logger.error(
                        f"Error in variable for model {m} backend {bk_name} registry {rg_name}"
                    )
                except Exception as e:
                    deploy = False
                    logger.error(
                        f"Error deploying {name} Model {m} not found in mlflow {e}"
                    )
        if deploy:
            logger.info(
                f"deploying seldon deployment {name} in namespace {GLOBAL_NAMESPACE}"
            )
            try:
                manifest = kube_client.get_namespaced_custom_object(
                    group=resource_group,
                    version="v1",
                    plural="seldondeployments",
                    namespace=GLOBAL_NAMESPACE,
                    name=rep_deploy_yaml["metadata"]["name"],
                )
                resourceVersion = manifest["metadata"]["resourceVersion"]
                manifest["metadata"].pop("creationTimestamp")
                manifest["metadata"].pop("generation")
                manifest["metadata"].pop("managedFields")
                manifest["metadata"].pop("resourceVersion")
                manifest["metadata"].pop("uid")
                manifest["metadata"].pop("namespace")
                manifest.pop("status")
                _name = rep_deploy_yaml["metadata"]["name"]
                if rep_deploy_yaml == manifest:
                    logger.info(f"seldon deployment {_name} in sync")
                else:
                    rep_deploy_yaml["metadata"]["resourceVersion"] = resourceVersion
                    kube_client.replace_namespaced_custom_object(
                        group=resource_group,
                        version="v1",
                        plural="seldondeployments",
                        body=rep_deploy_yaml,
                        name=_name,
                        namespace=GLOBAL_NAMESPACE,
                    )

            except KubeClient.rest.ApiException:
                kube_client.create_namespaced_custom_object(
                    group=resource_group,
                    version="v1",
                    plural="seldondeployments",
                    body=rep_deploy_yaml,
                    namespace=GLOBAL_NAMESPACE,
                )
            git_models.append(rep_deploy_yaml["metadata"]["name"])
    manifests = kube_client.list_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        plural="seldondeployments",
        namespace=GLOBAL_NAMESPACE,
        label_selector=f"app.kubernetes.io/mdc-type={controller_label_value}",
    )
    for i in manifests["items"]:
        model_name = i["metadata"]["name"]
        if model_name in git_models:
            logger.info(f"seldon deployment in sync {model_name}")
        else:
            kube_client.delete_namespaced_custom_object(
                group="machinelearning.seldon.io",
                version="v1",
                plural="seldondeployments",
                name=model_name,
                namespace=GLOBAL_NAMESPACE,
            )
