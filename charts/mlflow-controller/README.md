# mlflow-controller

![Version: 0.1.6](https://img.shields.io/badge/Version-0.1.6-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.6](https://img.shields.io/badge/AppVersion-0.1.6-informational?style=flat-square)

A Helm chart for Mlflow Deployment Controller

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` | affinity |
| envFromSecret | string | `""` | additional ENV from secret |
| fullnameOverride | string | `""` |  |
| gitops.BRANCH | string | `"main"` |  |
| gitops.deploymentLocation | string | `"/"` | deployment files folder location |
| gitops.enabled | bool | `true` | enable/disable gitops |
| gitops.gitPasswordSecretKey | string | `"githubtoken"` | git password secret key |
| gitops.gitPasswordSecretName | string | `"github-secret"` | git password secret name |
| gitops.gitUser | string | `"mdcadmin"` | git username |
| gitops.protocol | string | `"https"` | git repo protocol |
| gitops.repository | string | `"github.com/rocket9-code/model-deployments"` | git repository |
| image.pullPolicy | string | `"Always"` | image pull policy |
| image.repository | string | `"tachyongroup/mlflow-deployment-controller"` | image repository   |
| image.tag | string | `"mlflow-controller-0.1.6"` | image tag |
| imagePullSecrets | list | `[]` |  |
| mlflow.MLFLOW_TRACKING_URI | string | `"http://mlflow-service:5000"` | mlflow tracking uri |
| mlflow.backend | string | `"blob"` | Object Storage Used by mlflow supported gcs , blob , s3  |
| mlflow.enabled | bool | `true` |  |
| mlflow.namespace | string | `"staging"` | Namespace model to be deployed |
| mlflow.stage | string | `"Staging"` | Stage To be Tracked From Mlflow |
| mlserver | string | `"seldon"` | mlserver one of [seldon, kserve] |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` | node selector |
| podAnnotations | object | `{}` | pod annotations |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` | replica count |
| resources | object | `{}` | cpu memory resource config |
| securityContext | object | `{}` | security context |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `""` | If not set and create is true, a name is generated using the fullname template |
| tolerations | list | `[]` | tolerations |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.11.0](https://github.com/norwoodj/helm-docs/releases/v1.11.0)
