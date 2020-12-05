import dash
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = dcc.Graph(figure=px.line(x=[1, 2, 3, 4, 5], y=[4, 5, 6, 4, 6]))

app.run_server()
