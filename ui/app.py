import os

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from dash import Input, Output, dcc
from kubernetes import client as kube_client
from kubernetes import config

MLFLOW_NAMESPACE = os.getenv("namespace", "mlflow")
MDC_LABEL = os.getenv("MDC_LABEL", "mdc-staging")


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
)

navbar = dbc.NavbarSimple(
    [
        dbc.Button("Home", href="/", color="secondary", className="me-1"),
        dbc.Button("Logs", href="/logs", color="secondary", className="me-1"),
    ],
    brand="Mlflow Deployment Controller",
    color="primary",
    dark=True,
    className="mb-2",
)


def serve_layout():
    return html.Div(
        [navbar, dash.page_container],
        # fluid=True,
    )


app.layout = serve_layout

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
    df["models"] = [dcc.Link(f"{i}", href=f"/seldon/{i}") for i in df.models.values]
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return table


@app.callback(
    dash.dependencies.Output("table-deployments", "children"),
    [dash.dependencies.Input("interval-component", "n_intervals")],
)
def interval_deployment(n_intervals):
    return dataf()


@app.callback(
    dash.dependencies.Output("seldon-deployment", "children"),
    [dash.dependencies.Input("interval-component-seldon", "n_intervals")],
)
def internal_seldon_deployment(n_intervals):
    return []


@app.callback(Output("live-graph", "children"), [Input("graph-update", "n_intervals")])
def update_graph_scatter(n_intervals):
    print(n_intervals)
    v1 = kube_client.CoreV1Api()
    pod_name = v1.list_namespaced_pod(
        namespace=MLFLOW_NAMESPACE,
        label_selector=f"app.kubernetes.io/instance={MDC_LABEL}",
    )
    pod_name = pod_name.items[0].metadata.name
    lines = []
    lines = v1.read_namespaced_pod_log(
        name=pod_name,
        pretty=True,
        since_seconds=60,
        namespace=MLFLOW_NAMESPACE,
        follow=False,
        _preload_content=True,
    )
    # print(lines)
    return [
        html.Br(),
        html.H4("Controller Logs"),
        html.Plaintext(
            lines,
            style={
                "display": "inline-block",
                "fontSize": 15,
                # "verticalAlign": "top",
                "color": "white",
                "backgroundColor": "black",
            },
        ),
    ]


@app.callback(
    Output("collapse0", "is_open"),
    Output("collapse1", "is_open"),
    Output("collapse2", "is_open"),
    Output("collapse3", "is_open"),
    Output("collapse4", "is_open"),
    Output("collapse5", "is_open"),
    Output("collapse-button0", "n_clicks"),
    Output("collapse-button1", "n_clicks"),
    Output("collapse-button2", "n_clicks"),
    Output("collapse-button3", "n_clicks"),
    Output("collapse-button4", "n_clicks"),
    Output("collapse-button5", "n_clicks"),
    [
        Input("collapse-button0", "n_clicks"),
        Input("collapse-button1", "n_clicks"),
        Input("collapse-button2", "n_clicks"),
        Input("collapse-button3", "n_clicks"),
        Input("collapse-button4", "n_clicks"),
        Input("collapse-button5", "n_clicks"),
    ],
)
def toggle_collapse(n, n1, n2, n3, n4, n5):
    if n:
        return True, False, False, False, False, False, 0, 0, 0, 0, 0, 0
    if n1:
        return False, True, False, False, False, False, 0, 0, 0, 0, 0, 0
    if n2:
        return False, False, True, False, False, False, 0, 0, 0, 0, 0, 0
    if n3:
        return False, False, False, True, False, False, 0, 0, 0, 0, 0, 0
    if n4:
        return False, False, False, False, True, False, 0, 0, 0, 0, 0, 0
    if n5:
        return False, False, False, False, False, True, 0, 0, 0, 0, 0, 0
    return False, False, False, False, False, False, 0, 0, 0, 0, 0, 0


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=False)
