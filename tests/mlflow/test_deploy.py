import time

from kubernetes import client as KubeClient
from kubernetes import config

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
kube_client = KubeClient.CustomObjectsApi()
status = ""
timeout = time.time() + 60 * 10

while True:
    test = kube_client.get_namespaced_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        plural="seldondeployments",
        namespace="staging",
        name="mlflow",
    )
    status = test["status"]["state"]
    print(status)
    if status == "Available":
        break
    else:
        print(test["status"])
        time.sleep(30)
    if time.time() > timeout:
        # print(test)
        deploy_name = list(test["status"]["deploymentStatus"].keys())[0]
        kube_client = KubeClient.AppsV1Api()
        deployment = kube_client.read_namespaced_deployment(
            name=deploy_name, namespace="staging"
        )
        print(deployment)
        raise ("Timeout error")
