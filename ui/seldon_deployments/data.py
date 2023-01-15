import ast

import dash_bootstrap_components as dbc
from dash import html
from kubernetes import client as KubeClient
from kubernetes import config

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()


def pod_status(namespace, deploy_name):
    v1 = KubeClient.CoreV1Api()
    api_response = v1.list_namespaced_pod(namespace)
    for pod in api_response.items:
        if (pod.status.container_statuses is None) and (
            pod.status.init_container_statuses is None
        ):
            status = pod.status.conditions[0].message
            return (pod.metadata.name, status)

        if api_response.items[0].metadata.labels["app"] == deploy_name:
            status = pod.status.phase
            container_status = pod.status.container_statuses[0]

            if container_status.started is False or container_status.ready is False:
                waiting_state = container_status.state.waiting
                if (
                    waiting_state.message is not None
                    and "Error" in waiting_state.message
                ):
                    status = waiting_state.reason
            try:
                init_container_statuses = pod.status.init_container_statuses[0]
                if (
                    init_container_statuses.started is False
                    or init_container_statuses.ready is False
                ):
                    waiting_state = init_container_statuses.state.waiting
                    if (
                        waiting_state.message is not None
                        and "failed" in waiting_state.message
                    ):
                        status = waiting_state.reason
            except Exception as e:
                print(e)
                print("No init container found")
            if status == "CrashLoopBackOff":
                return (pod.metadata.name, status, waiting_state.message)


def dataf(
    name="mlflow-var", namespace="staging", seldon_url="https://seldon.mlops.wianai.com"
):
    v1 = KubeClient.CustomObjectsApi()
    manifest = v1.get_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        plural="seldondeployments",
        namespace=namespace,
        name=name,
    )
    models = []
    print(manifest["metadata"]["annotations"].keys())
    for _id in manifest["metadata"]["annotations"].keys():
        if ("mdc" in _id) and ("mlflow-stage" not in _id):
            models.append(manifest["metadata"]["annotations"][_id])
    model = [ast.literal_eval(i) for i in models]
    name = manifest["metadata"]["name"]
    external_url = f"{seldon_url}/seldon/{namespace}/{name}/api/v1.0/doc/"
    internal_url = manifest["status"]["address"]["url"]
    deploy_name = list(manifest["status"]["deploymentStatus"].keys())[0]
    kube_client = KubeClient.AppsV1Api()
    deployment = kube_client.read_namespaced_deployment(
        name=deploy_name, namespace=namespace
    )
    # label = deployment.metadata.labels["app"]
    status = ""
    for condition in deployment.status.conditions:
        if (condition.type == "Available") and (condition.status == "True"):
            status = "Available"
            status_button = dbc.Button(
                [html.I(className="bi bi-check-circle-fill me-2"), " Available"],
                color="success",
                disabled=True,
            )
            status_message = condition.message
            status_reason = condition.reason
        if status != "Available":
            if (condition.type == "Progressing") and (condition.status == "True"):
                status = "Progressing"
                status_message = condition.message
                status_reason = condition.reason
                status_button = dbc.Button(
                    [dbc.Spinner(size="sm"), " Progressing..."],
                    color="primary",
                    disabled=True,
                )
            elif (condition.type == "Progressing") and (condition.status == "False"):
                status = condition.reason
                status_message = condition.message
                status_reason = condition.reason
                status_button = dbc.Button(
                    [html.I(className="bi bi-x-octagon-fill me-2"), " Failed"],
                    color="danger",
                    disabled=True,
                )
    return (
        model,
        name,
        external_url,
        internal_url,
        status,
        status_message,
        status_reason,
        status_button,
        manifest,
    )
