<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Hellopmlops" />

  &#xa0;

 
</div>

<h1 align="center">Mlflow Deployment Controller</h1>


<br>

## :dart: About ##

Mlflow Does not have integration with model servers ( Ex: Seldon-core) for automated deployment of models when registered or promoted to different stages, Mlflow deployment controller tries to solve the problem. Mlflow deployment controller is a python based controller which periodically checks the state between mlflow and model server's CRD's in k8s and acts accordingly. Every stage in Mlflow needs a seperate controller as in real world we would have different clusters for each stage. you can configure the controller to manage state for certain stage based on the use case. To deploy models from mlflow you need to log a file called deploy.yaml with seldon-core deployment configurations


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

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/wianai" target="_blank">wianai</a>

&#xa0;

<a href="#top">Back to top</a>
