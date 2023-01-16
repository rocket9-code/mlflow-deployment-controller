import ast
import json
import os

import dash
import dash_bootstrap_components as dbc
import yaml
from dash import dcc, html
from kubernetes import config

from seldon_deployments.data import dataf

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()
GLOBAL_NAMESPACE = os.getenv("namespace", "staging")
SELDON_URL = os.getenv("seldon_url", "https://example.mlops.com")


def card_layout(deploy_name=None):
    (
        model_manifests,
        name,
        external_url,
        internal_url,
        status,
        status_message,
        status_reason,
        status_button,
        manifest,
    ) = dataf(name=deploy_name, namespace=GLOBAL_NAMESPACE, seldon_url=SELDON_URL)
    conditions = manifest["status"]["conditions"]
    collapses = []
    for i in range(len(conditions)):
        if conditions[i]["status"] == "False":
            color = "secondary"
        else:
            color = "success"
        type = conditions[i]["type"]
        try:
            reason = conditions[i]["reason"]
        except Exception as e:
            print(e)
            reason = type
        collapse = html.Div(
            [
                dbc.Button(
                    type,
                    id=f"collapse-button{i}",
                    className="mb-3",
                    color=color,
                    n_clicks=0,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody(reason)),
                    id=f"collapse{i}",
                    is_open=False,
                ),
            ]
        )
        collapses.append(collapse)

    res = ast.literal_eval(json.dumps(manifest))
    res = yaml.safe_dump(res, default_flow_style=False)
    code = f"```yaml{res}```"
    model_cards = []
    for i in model_manifests:
        model_card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(i["name"], className="card-title"),
                        dbc.ListGroup(
                            [
                                dbc.ListGroupItem(
                                    [
                                        html.A(
                                            "Run id: ", style={"font-weight": "bold"}
                                        ),
                                        html.A(i["run_id"]),
                                    ]
                                ),
                                dbc.ListGroupItem(
                                    [
                                        html.A(
                                            "Source: ", style={"font-weight": "bold"}
                                        ),
                                        html.A(i["source"]),
                                    ]
                                ),
                                dbc.ListGroupItem(
                                    [
                                        html.A(
                                            "Version: ", style={"font-weight": "bold"}
                                        ),
                                        html.A(i["version"]),
                                    ]
                                ),
                                dbc.ListGroupItem(
                                    [
                                        html.A(
                                            "Artifacu Uri: ",
                                            style={"font-weight": "bold"},
                                        ),
                                        html.A(i["artifact_uri"]),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        )
        model_cards.append(model_card)

    Overview_tab = dcc.Tab(
        label="Overview",
        children=[
            dbc.Card(
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [
                                html.A(
                                    "External Endpoint: ", style={"font-weight": "bold"}
                                ),
                                html.A(
                                    id="external_url",
                                    href=external_url,
                                    children=external_url,
                                    target="_blank",
                                ),
                                html.A(" "),
                                dcc.Clipboard(
                                    target_id="external_url",
                                    title="copy",
                                    style={
                                        "display": "inline-block",
                                        "fontSize": 20,
                                        "verticalAlign": "top",
                                    },
                                ),
                            ]
                        ),
                        dbc.ListGroupItem(
                            [
                                html.A(
                                    "Internal Endpoint: ", style={"font-weight": "bold"}
                                ),
                                html.A(
                                    id="internal_url",
                                    href=internal_url,
                                    children=internal_url,
                                    target="_blank",
                                ),
                                html.A(" "),
                                dcc.Clipboard(
                                    target_id="internal_url",
                                    title="copy",
                                    style={
                                        "display": "inline-block",
                                        "fontSize": 20,
                                        "verticalAlign": "top",
                                    },
                                ),
                            ]
                        ),
                        dbc.ListGroupItem(
                            [
                                html.A(
                                    "Status Message: ", style={"font-weight": "bold"}
                                ),
                                html.A(status_message),
                            ]
                        ),
                        dbc.ListGroupItem(
                            [
                                html.A(
                                    "Status Message: ", style={"font-weight": "bold"}
                                ),
                                html.A(status_reason),
                            ]
                        ),
                        dbc.ListGroupItem(
                            [
                                html.A("Status: ", style={"font-weight": "bold"}),
                                status_button,
                            ]
                        ),
                    ],
                    flush=True,
                ),
            )
        ]
        + collapses,
    )

    tabs = [
        Overview_tab,
        dcc.Tab(label="Details", children=model_cards),
        dcc.Tab(label="Yaml", children=[dcc.Markdown(str(code))]),
    ]
    if status == "Available":
        tabs.append(
            dcc.Tab(
                label="Doc",
                children=[
                    html.Iframe(
                        src=external_url, style={"height": "1067px", "width": "100%"}
                    )
                ],
            )
        )

    layout = html.Div([dash.html.H3(f"{name}"), dcc.Tabs(tabs)])
    return layout
