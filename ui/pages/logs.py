import dash
from dash import Output, Input  # , Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import glob
import yaml
import redis
import json
from kubernetes import client as KubeClient
from kubernetes import config
import kubernetes.client

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
            html.Div(id='live-graph'),
            dcc.Interval(
                id='graph-update',
                interval=1 * 10000,
                n_intervals=0
            ),
        ]
    )
