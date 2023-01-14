import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, register_page
from kubernetes import client as kube_client
from kubernetes import config

register_page(__name__, path="/")


try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()


def dataf():
    v1 = kube_client.CustomObjectsApi()
    manifests = v1.list_cluster_custom_object(
        group="machinelearning.seldon.io",
        version="v1",
        plural="seldondeployments",
        label_selector="app.kubernetes.io/managed-by=mdc",
    )
    model_name = []
    namespace = []
    state = []
    replicas = []
    for i in manifests["items"]:
        model_name.append(i["metadata"]["name"])
        namespace.append(i["metadata"]["namespace"])
        for _id in i["metadata"]["annotations"].keys():
            if "mdc" in _id:
                pass
        state.append(i["status"]["state"])
        deploy_name = list(i["status"]["deploymentStatus"].keys())[0]
        replicas.append(i["status"]["deploymentStatus"][deploy_name]["replicas"])
    df = pd.DataFrame(
        {
            "models": model_name,
            "namespace": namespace,
            "replicas": replicas,
            "state": state,
        }
    )
    return df


df = dataf()

df["models"] = [dcc.Link(f"{i}", href=f"/seldon/{i}") for i in df.models.values]


table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

layout = html.Div(
    [
        html.H5(
            "Seldon Deployments",
            className="mt-5",
        ),
        table,
    ]
)
