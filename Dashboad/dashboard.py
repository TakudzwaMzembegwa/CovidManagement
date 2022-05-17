from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from collections import OrderedDict
from dash import dcc, Dash, html, dash_table
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import dash_daq as daq
import plotly.graph_objs as go
import requests
import json

ppl_in_building = 0

# This loads the "cyborg" themed figure template from dash-bootstrap-templates library,
# adds it to plotly.io and makes it the default figure template.
load_figure_template("cyborg")

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


def get_users():
    # Gets a list of user in a building from the REST API
    users = requests.get(
        "https://covid-management-api.herokuapp.com/users")
    df = pd.DataFrame(pd.json_normalize(users.json()))
    return df


def get_desks():
    # Gets a list of desks in a building from the REST API
    desks = requests.get(
        "https://covid-management-api.herokuapp.com/building/uwc-cams-lab-c")
    desks = desks.json()['desks']
    desks = {n: [k for k in desks.keys() if desks[k] == n]
             for n in set(desks.values())}
    in_use = pd.DataFrame(OrderedDict([('In Use', desks.get('INUSE', []))]))
    free = pd.DataFrame(OrderedDict([('Free', desks.get('FREE', []))]))
    off = pd.DataFrame(OrderedDict([('Offline', desks.get('OFF', []))]))
    # Setting the number of ppl in the building
    global ppl_in_building
    ppl_in_building = in_use.shape[0]
    return in_use, free, off


# A dataframe of users in class
users_df = get_users()
# Dataframes of the desks in *in_use, free, off* state
in_use, free, off = get_desks()

graphs = html.Div(
    [
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        ),
        dbc.Row(
            [
                dbc.Col(dash_table.DataTable(
                    id="users_table",
                    columns=[
                        {"name": i.capitalize(), "id": i} for i in users_df.columns
                    ],
                    style_cell={'textAlign': 'center'},
                    fixed_rows={'headers': True},
                    style_table={'height': 500},
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{mask} = NO',
                            },
                            'backgroundColor': '#FF4136',
                            'color': 'white'
                        },
                    ],
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                ), lg=6),
                dbc.Col(dcc.Graph(id="gauge"), lg=6),
            ],
            className="mt-1",
        ),
        dbc.Row(
            [
                dbc.Col(dash_table.DataTable(
                    id="desk_in_use",
                    columns=[
                        {"name": i.capitalize(), "id": i} for i in in_use.columns
                    ],
                    style_cell={'textAlign': 'center'},
                    fixed_rows={'headers': True},
                    style_table={'height': 250},
                    style_header={
                        'backgroundColor': '#b51616',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_as_list_view=True,
                ), lg=2),
                dbc.Col(dash_table.DataTable(
                    id="desk_free",
                    columns=[
                        {"name": i.capitalize(), "id": i} for i in free.columns
                    ],
                    style_cell={'textAlign': 'center'},
                    fixed_rows={'headers': True},
                    style_table={'height': 250},
                    style_header={
                        'backgroundColor': '#1aab5d',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_as_list_view=True,
                ), lg=2),
                dbc.Col(dash_table.DataTable(
                    id="desk_offline",
                    columns=[
                        {"name": i.capitalize(), "id": i} for i in off.columns
                    ],
                    style_cell={'textAlign': 'center'},
                    fixed_rows={'headers': True},
                    style_table={'height': 250},
                    style_header={
                        'backgroundColor': '#5e5e5e',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_as_list_view=True,
                ), lg=2),
            ],
            className="mt-1",
        ),
    ]
)


@app.callback(
    Output('gauge', 'figure'),
    [Input('interval-component', "n_intervals")]
)
def update_indicator(value):
    fig = go.Figure(go.Indicator(
        value=ppl_in_building,
        domain={'x': [0.1, 0.9], 'y': [0.1, 1]},
        mode="gauge+number",
        title={'text': "Students in Lab C"},
        gauge={'axis': {'range': [None, 25]},
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 20}}))
    return fig


@app.callback(
    Output('users_table', 'data'),
    [Input('interval-component', "n_intervals")]
)
def update_users(value):
    return get_users().to_dict('records')


@app.callback(
    Output('desk_in_use', 'data'),
    Output('desk_free', 'data'),
    Output('desk_offline', 'data'),
    [Input('interval-component', "n_intervals")]
)
def update_desks(value):
    in_use, free, offline = get_desks()
    return in_use.to_dict('records'), free.to_dict('records'), offline.to_dict('records')


heading = html.H1("Covid Management",
                  style={'textAlign': 'center', 'backgroundColor': '#222694', 'color': 'white', 'font-weight': '20', 'font-size': '60px'})

app.layout = dbc.Container([heading, graphs], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True)
