import json
import logging
import re

from kubernetes import client as KubeClient
from kubernetes import config

from mlflow_controller.utils.var_extract import var_parser
from mlflow_controller.mlservers.rclone import rclone_source

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


def mlflow_model_search(lookup_key, json_dict, search_result=[]):
    if type(json_dict) == dict:
        for key, value in json_dict.items():
            if key == lookup_key:
                search_result.append(value)
            mlflow_model_search(lookup_key, value, search_result)
    elif type(json_dict) == list:
        for element in json_dict:
            mlflow_model_search(lookup_key, element, search_result)
    return search_result


def update_modeluris(json_para, search_para, replace_para):
    def decode_dict(a_dict):
        if search_para in a_dict.values():
            for key, value in a_dict.items():
                if value == search_para:
                    a_dict[key] = replace_para
        return a_dict

    return json.loads(json.dumps(json_para), object_hook=decode_dict)


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
            rep_deploy_yaml = deploy_yaml
            try:
                rep_deploy_yaml["metadata"]["annotations"]

            except:
                rep_deploy_yaml["metadata"]["annotations"] = {}
            try:
                rep_deploy_yaml["metadata"]["labels"]

            except:
                rep_deploy_yaml["metadata"]["labels"] = {}
            for m in models:
                try:
                    pattern = r"{{(.*?)}}"
                    model_jinja = re.search(pattern, m).group()
                    model_name, _, _ = var_parser(model_jinja)
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
                        f"mdc/mlflow-stage"
                    ] = stage
                    rep_deploy_yaml["metadata"]["labels"][
                        "app.kubernetes.io/mdc-type"
                    ] = controller_label_value
                    rep_deploy_yaml["metadata"]["labels"][
                        "app.kubernetes.io/managed-by"
                    ] = "mdc"
                    print(rep_deploy_yaml)

                except Exception as e:
                    name = rep_deploy_yaml["metadata"]["name"]
                    logger.error(
                        f"Error deploying {name} Model {m} not found in mlflow {e}"
                    )

        try:
            kube_client.create_namespaced_custom_object(
                group=resource_group,
                version="v1",
                plural="seldondeployments",
                body=rep_deploy_yaml,
                namespace=GLOBAL_NAMESPACE,
            )
        except KubeClient.rest.ApiException:
            kube_client.patch_namespaced_custom_object(
                group=resource_group,
                version="v1",
                plural="seldondeployments",
                body=rep_deploy_yaml,
                name=rep_deploy_yaml["metadata"]["name"],
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
            logger.info(f"model in sync {model_name}")
        else:
            kube_client.delete_namespaced_custom_object(
                group="machinelearning.seldon.io",
                version="v1",
                plural="seldondeployments",
                name=model_name,
                namespace=GLOBAL_NAMESPACE,
            )
