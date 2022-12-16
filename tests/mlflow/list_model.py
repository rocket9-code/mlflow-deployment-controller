import time

from kubernetes import client as KubeClient
from kubernetes import config
from mlflow.tracking import MlflowClient

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
kube_client = KubeClient.CustomObjectsApi()
mlflow_client = MlflowClient()
registered_models = mlflow_client.list_registered_models()
backend = "s3"
mlflow_models_metadata = {}
for registered_model in registered_models:
    for version in registered_model.latest_versions:
        if version.current_stage == "Staging":
            model_details = dict(version)
            model_run_id = model_details["run_id"]
            run_details = dict(mlflow_client.get_run(model_run_id).info)
            name = model_details["name"]
            model_template = f'{{{{ mlflow.{backend}["{name}"] }}}}'
            artifact_uri = run_details["artifact_uri"]
            mlflow_models_metadata[name] = {
                "name": name,
                "run_id": model_details["run_id"],
                "source": model_details["source"],
                "status": model_details["status"],
                "version": model_details["version"],
                "artifact_uri": artifact_uri,
            }
timeout = time.time() + 60 * 2
while True:
    if time.time() > timeout:
        raise ("Timeout error")
    manifest = kube_client.get_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        plural="seldondeployments",
        namespace="staging",
        name="mlflow-var-minio",
    )
    demo1 = manifest["spec"]["predictors"][0]["graph"]["children"][0]["modelUri"]
    demo2 = manifest["spec"]["predictors"][0]["graph"]["children"][0]["children"][0][
        "modelUri"
    ]
    demo3 = manifest["spec"]["predictors"][0]["graph"]["children"][1]["modelUri"]
    demo4 = manifest["spec"]["predictors"][0]["graph"]["modelUri"]
    if (
        (demo1 == mlflow_models_metadata["iris demo1"]["source"])
        & (demo2 == mlflow_models_metadata["iris demo2"]["source"])
        & (demo4 == mlflow_models_metadata["iris demo4"]["source"])
    ):
        print(demo1, demo2, demo3, demo4)
        break
