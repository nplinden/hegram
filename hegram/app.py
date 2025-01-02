from hegram.server import app
from hegram.build import df
from hegram.utils import binyanim_freq, root_table_data
import dash_bootstrap_components as dbc
from hegram.callbacks import *
from dash import html, dcc, dash_table
import pandas as pd

roots = sorted(list(df.index))

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

table = dash_table.DataTable(
    id="table",
    columns=[{"name": c, "id": c} for c in ["Rank", "Racine", "Classe", "Total"]],
    page_current=0,
    page_size=12,
    page_count=100,
    page_action="custom",
    style_cell={"fontSize": 20, "font-familiy": "monospace"},
    style_cell_conditional=[
        {
            "if": {"column_id": "Racine"},
            "font-family": "serif",
            "fontSize": 20,
        },
        {
            "if": {"column_id": "Classe"},
            "font-family": "serif",
            "fontSize": 20,
        },
    ],
    sort_action="custom",
    sort_mode="single",
    sort_by=[],
    tooltip_duration=None,
)

dropdown = dcc.Dropdown(
    ["Total", "Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal", "Classe"],
    id="dropdown",
    multi=True,
)

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1("Made by ניקולא לינדן"))),
        dbc.Row([dbc.Col(dropdown), dbc.Col()]),
        dbc.Row(
            [
                dbc.Col(table),
                dbc.Col(dcc.Graph("binyanim_root", figure=binyanim_freq(df))),
            ]
        ),
    ],
    style=CONTENT_STYLE,
)
