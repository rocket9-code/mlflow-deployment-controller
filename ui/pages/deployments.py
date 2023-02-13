from dash import dcc, html, register_page
from kubernetes import config

register_page(__name__, path="/")


try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()


layout = html.Div(
    [
        html.H5(
            "Seldon Deployments",
            className="mt-5",
        ),
        dcc.Interval(
            id="interval-component", interval=1 * 1000, n_intervals=0  # in milliseconds
        ),
        html.Div(id="table-deployments"),
    ]
)
