import dash
from dash import html

dash.register_page(__name__, path="/404")


layout = html.H1("404 Not found")
