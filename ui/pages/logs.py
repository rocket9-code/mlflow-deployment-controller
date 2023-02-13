import dash
import dash_core_components as dcc
import dash_html_components as html
from kubernetes import config

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()


def title():
    return f"Logs"


def description(ticker=None):
    return f"Controller Logs"


dash.register_page(
    __name__,
    path_template="/logs",
    title=title,
    description=description,
    path="/logs",
)


def layout(ticker=None, **other_unknown_query_strings):
    return html.Div(
        [
            html.Div(id="live-graph"),
            dcc.Interval(id="graph-update", interval=1 * 10000, n_intervals=0),
        ]
    )
