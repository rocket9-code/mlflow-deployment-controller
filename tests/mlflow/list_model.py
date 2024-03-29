import sys
import time

from git import Repo
from iris import main
from kubernetes import client as KubeClient
from kubernetes import config
from mlflow.tracking import MlflowClient
from termcolor import colored

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
kube_client = KubeClient.CustomObjectsApi()

timeout = time.time() + 60 * 2


print(colored("Test", "red"), colored("no1", "green"))


def test():
    backend = "s3"
    mlflow_client = MlflowClient()
    registered_models = mlflow_client.list_registered_models()
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
    while True:
        if sys.argv[1] == "seldon":
            manifest = kube_client.get_namespaced_custom_object(
                group="machinelearning.seldon.io",
                version="v1",
                plural="seldondeployments",
                namespace="staging",
                name="mlflow-var-minio",
            )
            demo1 = manifest["spec"]["predictors"][0]["graph"]["children"][0][
                "modelUri"
            ]
            demo2 = manifest["spec"]["predictors"][0]["graph"]["children"][0][
                "children"
            ][0]["modelUri"]
            demo3 = manifest["spec"]["predictors"][0]["graph"]["children"][1][
                "modelUri"
            ]
            demo4 = manifest["spec"]["predictors"][0]["graph"]["modelUri"]
            if (
                (demo1 == mlflow_models_metadata["iris demo1"]["source"])
                & (demo2 == mlflow_models_metadata["iris demo2"]["source"])
                & (demo4 == mlflow_models_metadata["iris demo4"]["source"])
            ):
                print(demo1, demo2, demo3, demo4)
                print("test passed", mlflow_models_metadata)
                break
        elif sys.argv[1] == "kserve":
            manifest = kube_client.get_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1beta1",
                plural="inferenceservices",
                namespace="staging",
                name="sklearn-iris-minio",
            )
            demo2 = manifest["spec"]["predictor"]["model"]["storageUri"]
            if demo2 == mlflow_models_metadata["iris demo2"]["source"]:
                print(demo2)
                print("test passed", mlflow_models_metadata)
                break
        if time.time() > timeout:
            print(mlflow_models_metadata)
            print(manifest)
            print(sys.argv[1])
            raise ("Timeout error")


test()

# Test transition

print(colored("Test", "red"), colored("no2", "green"))

for i in range(5):
    main(MODEL_NAME=f"iris demo{i}", version=2, stage="Staging")

test()

# Test removal
print(colored("Test", "red"), colored("no3", "green"))

if sys.argv[1] == "kserve":
    PATH_OF_GIT_REPO = "tests/repo-test"
    COMMIT_MESSAGE = "comment from python script"

    def git_push():
        import os

        os.remove("tests/repo-test/staging/kserve-s3.yaml")
        try:
            repo = Repo(PATH_OF_GIT_REPO)
            repo.git.add(update=True)
            repo.index.commit(COMMIT_MESSAGE)
            origin = repo.remote(name="origin")
            origin.push()
        except:
            print("Some error occured while pushing the code")

    git_push()

    while True:
        if time.time() > timeout:
            raise ("Timeout error")
        manifest = kube_client.list_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            plural="inferenceservices",
            namespace="staging",
        )
        model_names = []
        for i in manifest["items"]:
            model_names.append(i["metadata"]["name"])
        if "sklearn-iris-minio" in model_names:
            pass
        else:
            print(model_names)
            print("Deletion test passed")
            break

if sys.argv[1] == "seldon":
    PATH_OF_GIT_REPO = "tests/repo-test"
    COMMIT_MESSAGE = "comment from python script"

    def git_push():
        import os

        os.remove("tests/repo-test/staging/seldon-s3.yaml")
        try:
            repo = Repo(PATH_OF_GIT_REPO)
            repo.git.add(update=True)
            repo.index.commit(COMMIT_MESSAGE)
            origin = repo.remote(name="origin")
            origin.push()
        except:
            print("Some error occured while pushing the code")

    git_push()
    time.sleep(60)

    while True:
        if time.time() > timeout:
            raise ("Timeout error")
        manifest = kube_client.list_namespaced_custom_object(
            group="machinelearning.seldon.io",
            version="v1",
            plural="seldondeployments",
            namespace="staging",
        )
        model_names = []
        for i in manifest["items"]:
            model_names.append(i["metadata"]["name"])
        if "mlflow-var-minio" in model_names:
            pass
        else:
            print(model_names)
            print("Deletion test passed")
            break
