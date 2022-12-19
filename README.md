<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Hellopmlops" />

  &#xa0;

 
</div>

<h1 align="center">Mlflow Deployment Controller</h1>


<br>

## :dart: About ##

Mlflow Does not have integration with model servers ( Ex: Seldon-core) for automated deployment of models when registered or promoted to different stages, Mlflow deployment controller tries to solve this problem. Mlflow deployment controller is a python based controller which periodically checks the state between mlflow and model server's CRDs in k8s and acts accordingly. Every stage in Mlflow needs a separate controller as in the real world we would have different clusters for each stage. you can configure the controller to manage the state for a certain stage based on the use case. 

<img width="808" alt="Screenshot 2022-12-17 at 5 36 52 PM" src="https://user-images.githubusercontent.com/62284209/208241065-a297f111-6e2f-4e68-b430-a8b5ba455804.png">


## :rocket: Technologies ##

The following tools were used in this project:

- [Seldon-Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html)
- [Mlflow](https://www.mlflow.org/docs/latest/index.html)

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Helm](https://helm.sh/docs/helm/helm_install/) 

## :checkered_flag: Starting ##

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment f9n-code/mlflow-controller-deployment

```

## To Setup Deployment controller in different environments

### For Staging environment

Deployment controller will look for models logged with deploy.yaml in Mlflow Staging Environment and deploys the model in staging Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/mlflow-deployment-controller/

$ helm install mlflow-controller-deployment-staging  f9n-code/mlflow-controller-deployment --set mlflow.stage=Staging --set mlflow.namespace=staging

```

### For Production environment

Deployment controller will look models logged with deploy.yaml in Mlflow Production Environment and deploys the model in production Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment-production  f9n-code/mlflow-controller-deployment --set mlflow.stage=Production --set mlflow.namespace=production

```

Quick Start using argocd
---

Setup Mlflow and Mlflow controllers for different stages using argocd

```
kubectl apply -f  examples/argo-manifest
```

#### Log a Mlflow model with Seldon deployment configuration with the name deploy.yaml

  Model Uri parameter will be overwritten by controller so it can be left blank
  
<img width="783" alt="Screenshot 2022-07-10 at 6 26 01 PM" src="https://user-images.githubusercontent.com/62284209/178153282-9c107398-9f9f-4fc3-8bfc-ca9d5c9a9f3a.png">
  
  If any Model in mlflow is registered with deploy.yaml deployment controller will start deploying or managing the model server based on the config
  
<img width="1409" alt="Screenshot 2022-07-10 at 6 25 47 PM" src="https://user-images.githubusercontent.com/62284209/178153272-ae254b27-47ed-4251-aa69-07a305223aee.png">



Once the Model is logged with deploy.yaml deployment controller will deploy the model to the predefined namespace
Currently, the deployment controller does not have a UI(But it is in our roadmap ) so you can check the logs of the Mlflow deployment controller to see the model deployment  and any errors

        

```
kubectl logs -f deployment/mlflow-deploment-controller
```



<img width="1038" alt="Screenshot 2022-07-10 at 6 27 11 PM" src="https://user-images.githubusercontent.com/62284209/178153334-8909cecb-162e-4f86-ac22-f6cff0a7859d.png">


https://user-images.githubusercontent.com/62284209/182024746-1fa281ac-a388-467e-98cd-98e9f40a0ed0.mp4


## Gitops based deployment controller 

Gitops based deployment controller helps to version control seldon deployments as well as version control the models in ml registries in a automated way. 
Controller expects a templated variable in place of modelUri of the deplyment files which will be updated by the controller with the lastest version 
avalilable from the registies certain stage. For example if a controller is prod namespaces and production stage in mlflow and looking at the git repostory 
under folder production. it will get the manifest from the git repo's folder and the latest version from mlflow and deploy the model servers.



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
! helm repo add f9n-code https://f9n-code.github.io/helm-charts

! helm install mlflow-controller f9n-code/mlflow-controller-deployment  -n mlflow --set gitops.enabled=true  
```
Supported values 
registes: mlflow
backend: blob , gcs , s3

in future releases we can support azureml registries and databricks mlflow

Support matrix
| Ml endpoints | Seldon core |  Kserve |  Databricks | Azure ml | Vertex AI | SageMaker | 
|-----|---------|---------|---------|---------|---------|---------|
| Registries | | | | | |
| mlflow oss  gcs | :white_check_mark: |  :white_check_mark: |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| mlflow oss blob | :white_check_mark: |  :white_check_mark: |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| mlflow oss s3 | :white_check_mark: |  :white_check_mark: | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| databricks mlflow| ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| databricks azureml | ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 
| vertexai  registry | ✖️ (in roadmap) |  ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | ✖️ (in roadmap) | 


## To Setup Deployment controller in different environments with Gitops Enabled

### For Staging environment

Deployment controller will look for  yaml files staging folder and model in Mlflow Staging Environment and deploys the model in staging Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/mlflow-deployment-controller/

$ helm install mlflow-controller-deployment-staging  f9n-code/mlflow-controller-deployment --set gitops.enabled=true \ 
                                                      --set gitops.repository= github.com/rocket9-code/model-deployments  \
                                                      --set gitops.deploymentLocation=staging --set mlflow.stage=Staging \
                                                      --set mlflow.namespace=staging

```

### For Production environment

Deployment controller will look for  yaml files in production folder and model in Mlflow Production Environment and deploys the model in production Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment-production  f9n-code/mlflow-controller-deployment --set gitops.enabled=true  \
                                                          --set gitops.repository= github.com/rocket9-code/model-deployments \ 
                                                          --set gitops.deploymentLocation=production --set mlflow.stage=Production \
                                                          --set mlflow.namespace=production

```

quick start example is available at examples/gitops


## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/f9n-code" target="_blank">F9n</a>

&#xa0;

<a href="#top">Back to top</a>
