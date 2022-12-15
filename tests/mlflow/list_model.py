from mlflow.tracking import MlflowClient

client = MlflowClient()
print(client.list_registered_models())
