import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
)

test_coll = dbc.Collapse(
    dbc.Card(
        [
            # dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
            dbc.CardBody(
                [
                    html.H4("Card title", className="card-title"),
                    html.P(
                        "Some quick example text to build on the card title and "
                        "make up the bulk of the card's content.",
                        className="card-text",
                    ),
                    dbc.Button("Go somewhere", color="primary"),
                ]
            ),
        ],
        style={"width": "18rem"},
    ),
    id=f"collapsetest",
    is_open=False,
)


navbar = dbc.NavbarSimple(
    [dbc.Button("Home", href="/", color="secondary", className="me-1")],
    brand="Mlflow Deployment Controller",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,
)


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
