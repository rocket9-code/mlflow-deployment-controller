import sys
import time

from git import Repo
from kubernetes import client as KubeClient
from kubernetes import config
from mlflow.tracking import MlflowClient
from termcolor import colored

from iris import main

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
kube_client = KubeClient.CustomObjectsApi()
status = ""
timeout = time.time() + 60 * 2

while True:
    test = kube_client.get_namespaced_custom_object(group="machinelearning.seldon.io",
                                                    version="v1",
                                                    plural="seldondeployments",
                                                    namespace="staging",
                                                    name="mlflow")
    status = test["status"]["state"]
    print(status)
    if status == "Available":
        break
    else:
        print(test["status"])
        time.sleep(30)
    if time.time() > timeout:
        print(test)
        raise ("Timeout error")
