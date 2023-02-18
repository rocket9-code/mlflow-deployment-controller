import dash
from kubernetes import config
from seldon_deployments.card import card_layout

try:
    config.load_kube_config()
except config.ConfigException:
    config.load_incluster_config()


def title(ticker=None):
    return f"{ticker} Status"


def description(ticker=None):
    return f"Deployment status {ticker}"


dash.register_page(
    __name__,
    path_template="/seldon/<ticker>",
    title=title,
    description=description,
    path="/seldon/mlflow",
)


def layout(ticker=None, **other_unknown_query_strings):
    return card_layout(ticker)
