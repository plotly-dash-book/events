gapminder = px.data.gapminder()
gap_jp = gapminder[gapminder["country"] == "Japan"]
gap_cn = gapminder[gapminder["country"] == "China"]

app = JupyterDash(__name__)

app.layout = html.Div(
    [
        html.H1(
            "Dashハンズオン",
            style={
                "fontSize": "3rem",
                "color": "white",
                "textAlign": "center",
                "backgroundColor": "black",
            },
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": i, "value": i} for i in gapminder.continent.unique()
                    ],
                    value="Asia",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": i, "value": i} for i in gapminder.continent.unique()
                    ],
                    value="Europe",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": i, "value": i} for i in gapminder.continent.unique()
                    ],
                    value="Americas",
                ),
            ],
            style={"width": "33%", "display": "inline-block", "paddingBottom": "30%"},
        ),
        html.Div(
            [dcc.Graph(figure=px.scatter(gap_jp, x="year", y="gdpPercap"))],
            style={"width": "33%", "display": "inline-block"},
        ),
        html.Div(
            [dcc.Graph(figure=px.scatter(gap_cn, x="year", y="pop"))],
            style={"width": "33%", "display": "inline-block"},
        ),
    ]
)

app.run_server(mode="inline")
