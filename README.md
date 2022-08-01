<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Hellopmlops" />

  &#xa0;

 
</div>

<h1 align="center">Mlflow Deployment Controller</h1>


<br>

## :dart: About ##

Mlflow Does not have integration with model servers ( Ex: Seldon-core) for automated deployment of models when registered or promoted to different stages, Mlflow deployment controller tries to solve this problem. Mlflow deployment controller is a python based controller which periodically checks the state between mlflow and model server's CRDs in k8s and acts accordingly. Every stage in Mlflow needs a separate controller as in the real world we would have different clusters for each stage. you can configure the controller to manage the state for a certain stage based on the use case. 


![Mlflow Deployment controller drawio (1)](https://user-images.githubusercontent.com/62284209/180271769-d24c58bb-7a37-416d-b110-f860bee951df.png)



## :rocket: Technologies ##

The following tools were used in this project:

- [Seldon-Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html)
- [Mlflow](https://www.mlflow.org/docs/latest/index.html)

## :white_check_mark: Requirements ##

Before starting :checkered_flag:, you need to have [Helm](https://helm.sh/docs/helm/helm_install/) 

## :checkered_flag: Starting ##

```bash
$ helm repo add wianai https://HelloMLOps.github.io/helm-charts

$ helm install mlflow-controller-deployment wianai/mlflow-controller-deployment

```
## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| mlflow.MLFLOW_TRACKING_URI | string | `"http://mlflow-service.mlflow.svc.cluster.local:5000"` | Mlflow URI |
| mlflow.stage | string | `"Production"` | Stage To be Tracked From Mlflow  |
| mlflow.namespace | string | `"default"` | Namespace model to be deployed |
| mlflow.cloud | string | `"azure_blob"` | Object Storage Used by mlflow supported gcp-bucket , azure_blob (aws_s3 in roadmap) |

## Compatabilty

| cloud | storage | support status | 
|-----|------|---------|
| gcp | buckets | :white_check_mark: | 
| azure | blob | :white_check_mark: | 
| aws | s3 | ✖️ |

| Model Servers | support status | 
|-----|---------|
| Seldon-Core  | :white_check_mark: | 
| Kserve | ✖️ (in roadmap) | 
| BentoML | ✖️ (in roadmap) | 


## To Setup Deployment controller in different environments

### For Staging environment

Deployment controller will look for models logged with deploy.yaml in Mlflow Staging Environment and deploys the model in staging Namespace

```bash
$ helm repo add wianai https://wianai.github.io/mlflow-deployment-controller/

$ helm install mlflow-controller-deployment-staging  wianai/mlflow-controller-deployment --set mlflow.stage=Staging --set mlflow.namespace=staging

```

### For Production environment

Deployment controller will look models logged with deploy.yaml in Mlflow Production Environment and deploys the model in production Namespace

```bash
$ helm repo add wianai https://HelloMLOps.github.io/helm-charts

$ helm install mlflow-controller-deployment-production  wianai/mlflow-controller-deployment --set mlflow.stage=Production --set mlflow.namespace=production

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


## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/wianai" target="_blank">wianai</a>

&#xa0;

<a href="#top">Back to top</a>
