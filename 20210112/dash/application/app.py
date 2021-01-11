import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH

import plotly.express as px
import pandas as pd

## DATA FROM https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series


data_urls = {
    "cases": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
    "death": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
    "recovery": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
}


def _read_and_melt(url):
    df = pd.read_csv(url).drop("Province/State", axis=1)
    df = df.melt(id_vars=["Country/Region", "Lat", "Long"])
    df["variable"] = pd.to_datetime(df["variable"])
    return df


def _update_data(df):
    data = pd.DataFrame()
    for country in df["Country/Region"].unique():
        df_country = df[df["Country/Region"] == country].copy().reset_index(drop=True)
        first_value = df_country["value"][0]
        counts_list = list(df_country["value"].diff().values)
        counts_list[0] = first_value
        df_country["counts"] = counts_list
        data = pd.concat([data, df_country])
    return data


def read_john_data(url):
    df = _read_and_melt(url)
    df = _update_data(df)
    return df


def _mapdata_to_weekly(df):
    df = df.set_index("variable")
    df = df.resample("W").last()
    df = df.drop("counts", axis=1)
    df = df.reset_index()
    df["variable"] = df["variable"].astype("str")
    return df


def mapdata(df):
    data = pd.DataFrame()
    for country in df["Country/Region"].unique():
        country_df = df[df["Country/Region"] == country]
        country_df = _mapdata_to_weekly(country_df)
        data = pd.concat([data, country_df])
    return data


cases = read_john_data("data/cases.csv")
death = read_john_data("data/death.csv")
recovery = read_john_data("data/recovery.csv")
cases_map = mapdata(cases)
death_map = mapdata(death)
recovery_map = mapdata(recovery)
cases_map["data_type"] = "cases"
death_map["data_type"] = "death"
recovery_map["data_type"] = "recovery"
all_data = pd.concat([cases_map, death_map, recovery_map])

mapbox = "your-token"
px.set_mapbox_access_token(mapbox)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("COVID-19 Time series Data"),
                html.P(
                    "Data from Johns Hopkins University: ", style={"fontSize": "2.5rem"}
                ),
                html.A(
                    "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series",
                    href="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series",
                ),
            ],
            style={
                "marginBottom": "2%",
                "backgroundColor": "#5feb4d",
                "padding": "3%",
                "borderRadius": "20px",
            },
        ),
        html.Div(
            [
                html.H3("国ごとのデータ"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="drop1",
                            options=[
                                {"label": i, "value": i}
                                for i in ["感染者数", "死亡者数", "回復者数"]
                            ],
                            value="感染者数",
                        ),
                        dcc.Dropdown(
                            id="drop2",
                            options=[
                                {"label": i, "value": i}
                                for i in cases["Country/Region"].unique()
                            ],
                            value=["Japan"],
                            multi=True,
                        ),
                        dcc.RadioItems(
                            id="graph_radio",
                            options=[{"label": s, "value": s} for s in ["新規", "累計"]],
                            value="新規",
                        ),
                    ]
                ),
                dcc.Graph(id="first_graph"),
                dcc.Graph(
                    id="map_graph", style={"width": "65%", "display": "inline-block"}
                ),
                dcc.Graph(
                    id="callback_graph",
                    style={"width": "35%", "display": "inline-block"},
                ),
                html.H1(id="test"),
            ],
            style={
                "marginBottom": "2%",
                "backgroundColor": "#5feb4d",
                "padding": "3%",
                "borderRadius": "20px",
            },
        ),
        # html.Div(
        #     [
        #         html.Div(
        #             [
        #                 html.H3("国ごとのデータ（パターン・マッチング・コールバック）"),
        #                 html.Button(id="junku_button", children="PUSHME", n_clicks=0),
        #                 html.Div(id="add_layout", children=[]),
        #             ]
        #         )
        #     ],
        #     style={
        #         "backgroundColor": "#5feb4d",
        #         "padding": "3%",
        #         "borderRadius": "20px",
        #     },
        # ),
    ],
    style={"padding": "5%", "backgroundColor": "#17be06"},
)


@app.callback(
    Output("first_graph", "figure"),
    Output("map_graph", "figure"),
    Input("drop1", "value"),
    Input("drop2", "value"),
    Input("graph_radio", "value"),
)
def update_graph(type_select, cnt_select, graph_select):
    if type_select == "死亡者数":
        death_data = death[death["Country/Region"].isin(cnt_select)]
        if graph_select == "新規":
            return (
                px.line(death_data, x="variable", y="counts", color="Country/Region"),
                px.scatter_mapbox(
                    death_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )
        else:
            return (
                px.line(death_data, x="variable", y="value", color="Country/Region"),
                px.scatter_mapbox(
                    death_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )
    elif type_select == "回復者数":
        recovery_data = recovery[recovery["Country/Region"].isin(cnt_select)]
        if graph_select == "新規":
            return (
                px.line(
                    recovery_data, x="variable", y="counts", color="Country/Region"
                ),
                px.scatter_mapbox(
                    recovery_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )
        else:
            return (
                px.line(recovery_data, x="variable", y="value", color="Country/Region"),
                px.scatter_mapbox(
                    recovery_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )
    else:
        cases_data = cases[cases["Country/Region"].isin(cnt_select)]
        if graph_select == "新規":
            return (
                px.line(cases_data, x="variable", y="counts", color="Country/Region"),
                px.scatter_mapbox(
                    cases_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )
        else:
            return (
                px.line(cases_data, x="variable", y="value", color="Country/Region"),
                px.scatter_mapbox(
                    cases_map,
                    lat="Lat",
                    lon="Long",
                    size="value",
                    animation_frame="variable",
                    color="value",
                    hover_name="Country/Region",
                    zoom=1,
                    size_max=60,
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    height=800,
                    title=f"マップ表示(累計値: {type_select})",
                    template={"layout": {"clickmode": "event+select"}},
                ),
            )


@app.callback(
    Output("callback_graph", "figure"),
    Input("map_graph", "selectedData"),
    Input("drop1", "value"),
)
def update_graph(selectedData, selected_value):
    if selectedData is None:
        selectedData = {"points": [{"hovertext": "Japan"}]}
    country_list = list()
    for one_dict in selectedData["points"]:
        country_list.append(one_dict["hovertext"])
    if selected_value == "死亡者数":
        death_df = death[death["Country/Region"].isin(country_list)]
        return px.line(
            death_df,
            x="variable",
            y="value",
            color="Country/Region",
            title=f"選択国の{selected_value}(累計値: SHIFT+クリック)",
            height=800,
        )
    elif selected_value == "回復者数":
        recovery_df = recovery[recovery["Country/Region"].isin(country_list)]
        return px.line(
            recovery_df,
            x="variable",
            y="value",
            color="Country/Region",
            title=f"選択国の{selected_value}(累計値: SHIFT+クリック)",
            height=800,
        )
    else:
        cases_df = cases[cases["Country/Region"].isin(country_list)]
        return px.line(
            cases_df,
            x="variable",
            y="value",
            color="Country/Region",
            title=f"選択国の{selected_value}(累計値: SHIFT+クリック)",
            height=800,
        )


# @app.callback(
#     Output("add_layout", "children"),
#     Input("junku_button", "n_clicks"),
#     State("add_layout", "children"),
# )
# def update_layout(n_clicks, layout_children):
#     append_layout = html.Div(
#         [
#             dcc.Dropdown(
#                 id={"type": "count_select_drop", "index": n_clicks},
#                 options=[
#                     {"value": i, "label": i} for i in cases["Country/Region"].unique()
#                 ],
#                 value=cases["Country/Region"].unique()[n_clicks],
#             ),
#             dcc.RadioItems(
#                 id={"type": "count_select_radio", "index": n_clicks},
#                 options=[{"value": i, "label": i} for i in ["Linear", "Log"]],
#                 value="Linear",
#             ),
#             dcc.Graph(id={"type": "count_select_graph", "index": n_clicks}),
#         ],
#         style={"width": "46%", "padding": "2%", "display": "inline-block"},
#     )
#     layout_children.append(append_layout)
#     return layout_children


# @app.callback(
#     Output({"type": "count_select_graph", "index": MATCH}, "figure"),
#     Input({"type": "count_select_drop", "index": MATCH}, "value"),
#     Input({"type": "count_select_radio", "index": MATCH}, "value"),
# )
# def update_country_graph(selected_country, selected_radio_value):
#     if selected_country is None:
#         dash.exceptions.PreventUpdate
#     selected_country_data = all_data[all_data["Country/Region"] == selected_country]
#     if selected_radio_value == "Log":
#         return px.line(
#             selected_country_data,
#             x="variable",
#             y="value",
#             color="data_type",
#             log_y=True,
#         )
#     return px.line(selected_country_data, x="variable", y="value", color="data_type",)


if __name__ == "__main__":
    app.run_server(debug=True)
