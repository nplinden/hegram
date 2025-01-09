from hegram.server import app
from hegram.components.textbox import textbox
from hegram.components.menu import menu
import dash_bootstrap_components as dbc
from hegram.callbacks import *
from dash import html, dcc, dash_table

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

table = dash_table.DataTable(
    id="table",
    columns=[{"name": c, "id": c} for c in ["Rank", "Root", "Class", "Total"]],
    page_current=0,
    page_size=12,
    page_count=100,
    page_action="custom",
    style_cell={"fontSize": 20, "font-familiy": "monospace"},
    style_cell_conditional=[
        {
            "if": {"column_id": "Root"},
            "font-family": "serif",
            "fontSize": 20,
        },
        {
            "if": {"column_id": "Class"},
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
    ["Total", "Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal", "Class"],
    id="dropdown",
    multi=True,
    className="dropdown",
)

definition_markdown = dcc.Markdown(
    """
""",
    id="definition",
    className="textbox-text",
)

graph = dcc.Graph("binyanim_root", figure=occurences.binyanim_bar_graph())

core = dbc.Container(
    [
        dbc.Row(
            textbox(
                "An app for hebrew grammar analysis in the Hebrew Bible",
                "Hegram by ניקולא לינדן",
            ),
            class_name="textbox-container",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div("Verbal Roots", className="menu-title"),
                            dropdown,
                            table,
                        ],
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div("Occurences", className="menu-title"),
                            graph,
                        ],
                    ),
                ),
            ],
            className="graph-row",
        ),
        dbc.Row(
            dbc.Col(html.Div([definition_markdown], className="textbox-container"))
        ),
    ]
)

app.layout = html.Div(children=[core])
