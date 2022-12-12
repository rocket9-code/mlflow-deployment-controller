import json
import logging

from kubernetes import client as KubeClient
from kubernetes import config

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


def sync(deploy_yamls, model_metadata, stage, GLOBAL_NAMESPACE, controller_label_value):
    git_models = []
    for deploy_yaml in deploy_yamls:
        resource_group = deploy_yaml["apiVersion"].split("/")[0]
        if resource_group == "machinelearning.seldon.io":
            models = list(
                set(mlflow_model_search("modelUri", deploy_yaml, search_result=[]))
            )
            logger.info(models)
            logger.info(model_metadata)
            rep_deploy_yaml = deploy_yaml
            try:
                rep_deploy_yaml["metadata"]["annotations"]
            except:
                rep_deploy_yaml["metadata"]["annotations"] = {}
            for m in models:
                try:
                    model = model_metadata[m]
                    run_id = model["run_id"]
                    rep_deploy_yaml = update_modeluris(
                        rep_deploy_yaml, deploy_yaml, model["source"]
                    )
                    rep_deploy_yaml["metadata"]["annotations"][
                        f"mdc/mlflow-{run_id}"
                    ] = str(model)
                    rep_deploy_yaml["metadata"]["annotations"][
                        f"mdc/mlflow-stage"
                    ] = stage
                    rep_deploy_yaml["metadata"]["labels"][
                        "app.kubernetes.io/managed-by"
                    ] = controller_label_value
                except:
                    name = rep_deploy_yaml["metadata"]["name"]
                    logger.error(
                        f"Error deploying {name} Model {m} not found in mlflow"
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
        label_selector=f"app.kubernetes.io/managed-by={controller_label_value}",
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
