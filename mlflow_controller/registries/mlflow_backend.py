import logging
import os
import re
from io import BytesIO

import boto3
import yaml
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from google.cloud.storage import Client as GoogleClient

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


class Artifact:
    def __init__(self):
        print("Class Artifact initalized")
        self.mlflow_deploy_config = "deploy.yaml"

    def gcp_bucket(self, artifact_uri):
        google_client = GoogleClient()
        bucket = artifact_uri.split("/")[2]
        object_name = (
            "/".join(artifact_uri.split("/")[3:]) + f"/{self.mlflow_deploy_config}"
        )
        bucket = google_client.get_bucket(bucket)
        blob = bucket.get_blob(object_name)
        downloaded_file = blob.download_as_text(encoding="utf-8")
        deploy_yaml = yaml.safe_load(downloaded_file)
        return deploy_yaml

    def azure_blob(self, artifact_uri):
        acc_name_re = r"(?<=\/\/)(.*)(?=\@)"
        container_re = r"(?<=\@)(.*)(?=[\.])"
        container = re.search(acc_name_re, artifact_uri).group(1)
        acc_name = re.search(container_re, artifact_uri).group(1).split(".")[0]
        STORAGEACCOUNTURL = f"https://{acc_name}.blob.core.windows.net"
        default_credential = DefaultAzureCredential()
        blob_service_client_instance = BlobServiceClient(
            account_url=STORAGEACCOUNTURL, credential=default_credential
        )
        blob_location = (
            "/".join(artifact_uri.split("blob.core.windows.net")[1].split("/")[1:-1])
            + f"/artifacts/{self.mlflow_deploy_config}"
        )
        blob_client_instance = blob_service_client_instance.get_blob_client(
            container, blob_location, snapshot=None
        )
        blob_data = blob_client_instance.download_blob()
        bl = blob_data.readall()
        deploy_yaml = yaml.load(bl, Loader=yaml.FullLoader)
        return deploy_yaml

    def aws_s3(self, artifact_uri):
        session = boto3.Session()
        s3_client = session.client("s3")
        path_parts = artifact_uri.replace("s3://", "").split("/")
        bucket = path_parts.pop(0)
        key = "/".join(path_parts) + "/deploy.yaml"
        f = BytesIO()
        s3_client.download_fileobj(bucket, key, f)

        deploy_yaml = yaml.load(f.getvalue(), Loader=yaml.FullLoader)
        return deploy_yaml
