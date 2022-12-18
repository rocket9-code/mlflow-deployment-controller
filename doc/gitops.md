## Gitops based deployment controller 

Gitops based deployment controller helps to version control seldon deployments as well as version control the models in ml registries in a automated way. 
Controller expected a templated variable in place of modelUri of the deplyment files which will be updated by the controller with the lastest version 
avalilable from the registies certain stage. For example if a controller is prod namespaces and production stage in mlflow and looking at the git repostory 
under folder production. it will get the manifest from the git repo's folder and the latest version from mlflow and deploy the model servers.

<img width="811" alt="Screenshot 2022-12-17 at 6 33 32 PM" src="https://user-images.githubusercontent.com/62284209/208243176-62c032ab-870a-4ebf-badc-cc4f2e5a025f.png">

Create a new repository for deployment controller and create a seldon manifest in the place of modelUri use this template '{{ mlflow.blob["iris demo1"] }}' 
to specify the model metadata the syntax of the template is {{ registry.backend["MODEL NAME IN REGISTRY"]}}

Example deployment file deploying multiple models in seldon-core 
<details>
  <summary>Expand me</summary>
  
 ```
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: mlflow-var
spec:
  name: iris
  predictors:
  - graph:
      children:
        - name: step-one
          modelUri: '{{ mlflow.blob["iris demo1"] }}'
          envSecretRefName: seldon-rclone-secret
          implementation: MLFLOW_SERVER
          type: MODEL
          children: 
              - name: step-two
                modelUri: '{{ mlflow.blob["iris demo2"] }}'
                envSecretRefName: seldon-rclone-secret
                implementation: MLFLOW_SERVER
                type: MODEL
                children: []
        - name: step-three
          implementation: MLFLOW_SERVER
          modelUri: '{{ mlflow.blob["iris demo3"] }}'
          envSecretRefName: seldon-rclone-secret
          type: MODEL
          children: []
      implementation: MLFLOW_SERVER
      modelUri: '{{ mlflow.blob["iris demo4"] }}'
      envSecretRefName: seldon-rclone-secret
      logger:
        url: http://broker-ingress.knative-eventing.svc.cluster.local/demo/default
        mode: all
      name: classifier
    name: default
    replicas: 1
```
</details>


The template values are updated by the controller with the latest version the registry as below and submitted to the kubernetes api

<details>
  <summary>Expand me</summary>
  
 ```
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: mlflow-var
  namespace: staging
spec:
  name: iris
  predictors:
    - graph:
        children:
          - children:
              - children: []
                envSecretRefName: seldon-rclone-secret
                implementation: MLFLOW_SERVER
                modelUri: '{{ mlflow.blob["iris demo2"] }}'
                name: step-two
                type: MODEL
            envSecretRefName: seldon-rclone-secret
            implementation: MLFLOW_SERVER
            modelUri: '{{ mlflow.blob["iris demo1"] }}'
            name: step-one
            type: MODEL
          - children: []
            envSecretRefName: seldon-rclone-secret
            implementation: MLFLOW_SERVER
            modelUri: >-
              wasbs://artifacts/mlflow/10/262bee84b7dd4b039973084383880b57/artifacts/model
            name: step-three
            type: MODEL
        envSecretRefName: seldon-rclone-secret
        implementation: MLFLOW_SERVER
        logger:
          mode: all
          url: >-
            http://broker-ingress.knative-eventing.svc.cluster.local/demo/default
        modelUri: '{{ mlflow.blob["iris demo4"] }}'
        name: classifier
      name: default
```
</details>


To enable gitops in the controller 

```
! git clone -b gitops-enable https://github.com/rocket9-code/mlflow-deployment-controller

! helm install mlflow-controller mlflow-deployment-controller/charts/mlflow-controller  -n mlflow --set gitops.enabled=true  
```
Supported values 
registes: mlflow
backend: blob , gcs , s3

in future releases we can support azureml registries and databricks mlflow

Support matrix
| Ml endpoints | Seldon core |  Kserve |  Databricks | Azure ml | Vertex AI | SageMaker | 
|-----|---------|---------|---------|---------|---------|---------|
| Registries | | | | | |
| mlflow oss  gcs | :white_check_mark: |  ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| mlflow oss blob | :white_check_mark: |  ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| mlflow oss s3 | :white_check_mark: |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| databricks mlflow| ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| databricks azureml | ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| vertexai  registry | ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 


## To Setup Deployment controller in different environments with Gitops Enabled

### For Staging environment

Deployment controller will look for models logged with deploy.yaml in Mlflow Staging Environment and deploys the model in staging Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/mlflow-deployment-controller/

$ helm install mlflow-controller-deployment-staging  f9n-code/mlflow-controller-deployment --set gitops.enabled=true \ 
                                                      --set gitops.repository= github.com/rocket9-code/model-deployments  \
                                                      --set gitops.deploymentLocation=staging --set mlflow.stage=Staging \
                                                      --set mlflow.namespace=staging

```

### For Production environment

Deployment controller will look models logged with deploy.yaml in Mlflow Production Environment and deploys the model in production Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment-production  f9n-code/mlflow-controller-deployment --set gitops.enabled=true  \
                                                          --set gitops.repository= github.com/rocket9-code/model-deployments \ 
                                                          --set gitops.deploymentLocation=production --set mlflow.stage=Production \
                                                          --set mlflow.namespace=production

```
