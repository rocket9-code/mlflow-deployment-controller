from mlflow_controller.gitops import GitopsMDC
from mlflow_controller.mlflow_direct import DeployConroller

# controller = GitopsMDC()
# controller.gitops_mlflow_controller()

controller = DeployConroller()
controller.deploy_controller()
