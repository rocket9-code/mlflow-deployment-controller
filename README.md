# README

![Hellopmlops](.github/app.gif)

&#x20;

## Mlflow Deployment Controller



\


### :dart: About

Mlflow Does not have integration with model servers ( Ex: Seldon-core) for automated deployment of models when registered or promoted to different stages, Mlflow deployment controller tries to solve this problem. Mlflow deployment controller is a python based controller which periodically checks the state between mlflow and model server's CRDs in k8s and acts accordingly. Every stage in Mlflow needs a separate controller as in the real world we would have different clusters for each stage. you can configure the controller to manage the state for a certain stage based on the use case.

![Mlflow Deployment controller drawio (1)](https://user-images.githubusercontent.com/62284209/180271769-d24c58bb-7a37-416d-b110-f860bee951df.png)

### :rocket: Technologies

The following tools were used in this project:

* [Seldon-Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html)
* [Mlflow](https://www.mlflow.org/docs/latest/index.html)

### :white\_check\_mark: Requirements

Before starting :checkered\_flag:, you need to have [Helm](https://helm.sh/docs/helm/helm\_install/)

### :checkered\_flag: Starting

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment f9n-code/mlflow-controller-deployment

```

### Values

| Key                          | Type   | Default                                                 | Description                                                                           |
| ---------------------------- | ------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| mlflow.MLFLOW\_TRACKING\_URI | string | `"http://mlflow-service.mlflow.svc.cluster.local:5000"` | Mlflow URI                                                                            |
| mlflow.stage                 | string | `"Production"`                                          | Stage To be Tracked From Mlflow                                                       |
| mlflow.namespace             | string | `"default"`                                             | Namespace model to be deployed                                                        |
| mlflow.cloud                 | string | `"azure_blob"`                                          | Object Storage Used by mlflow supported gcp-bucket , azure\_blob (aws\_s3 in roadmap) |

### Compatabilty

| cloud | storage | support status       |
| ----- | ------- | -------------------- |
| gcp   | buckets | :white\_check\_mark: |
| azure | blob    | :white\_check\_mark: |
| aws   | s3      | :white\_check\_mark: |

| Model Servers | support status       |
| ------------- | -------------------- |
| Seldon-Core   | :white\_check\_mark: |
| Kserve        | ✖️ (in roadmap)      |
| BentoML       | ✖️ (in roadmap)      |

### To Setup Deployment controller in different environments

#### For Staging environment

Deployment controller will look for models logged with deploy.yaml in Mlflow Staging Environment and deploys the model in staging Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/mlflow-deployment-controller/

$ helm install mlflow-controller-deployment-staging  f9n-code/mlflow-controller-deployment --set mlflow.stage=Staging --set mlflow.namespace=staging

```

#### For Production environment

Deployment controller will look models logged with deploy.yaml in Mlflow Production Environment and deploys the model in production Namespace

```bash
$ helm repo add f9n-code https://f9n-code.github.io/helm-charts

$ helm install mlflow-controller-deployment-production  f9n-code/mlflow-controller-deployment --set mlflow.stage=Production --set mlflow.namespace=production

```

### Quick Start using argocd

Setup Mlflow and Mlflow controllers for different stages using argocd

```
kubectl apply -f  examples/argo-manifest
```

**Log a Mlflow model with Seldon deployment configuration with the name deploy.yaml**

Model Uri parameter will be overwritten by controller so it can be left blank

![Screenshot 2022-07-10 at 6 26 01 PM](https://user-images.githubusercontent.com/62284209/178153282-9c107398-9f9f-4fc3-8bfc-ca9d5c9a9f3a.png)

If any Model in mlflow is registered with deploy.yaml deployment controller will start deploying or managing the model server based on the config

![Screenshot 2022-07-10 at 6 25 47 PM](https://user-images.githubusercontent.com/62284209/178153272-ae254b27-47ed-4251-aa69-07a305223aee.png)

Once the Model is logged with deploy.yaml deployment controller will deploy the model to the predefined namespace Currently, the deployment controller does not have a UI(But it is in our roadmap ) so you can check the logs of the Mlflow deployment controller to see the model deployment and any errors

```
kubectl logs -f deployment/mlflow-deploment-controller
```

![Screenshot 2022-07-10 at 6 27 11 PM](https://user-images.githubusercontent.com/62284209/178153334-8909cecb-162e-4f86-ac22-f6cff0a7859d.png)

https://user-images.githubusercontent.com/62284209/182024746-1fa281ac-a388-467e-98cd-98e9f40a0ed0.mp4

### :memo: License

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.

Made with :heart: by [F9n](https://github.com/f9n-code)

&#x20;

[Back to top](./#top)
