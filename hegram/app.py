from hegram.callbacks import (
    update_binyanim_bar_graph,
    update_barchart_series,
    update_table,
    update_definition,
    update_table_page_number,
)

import dash_mantine_components as dmc
from dash import html, dcc, dash_table
from hegram.occurences import occurences

from flask import Flask
from dash import Dash, _dash_renderer

_dash_renderer._set_react_version("18.2.0")
server = Flask("Hebrew Grammar")
app = Dash(server=server, external_stylesheets=[dmc.styles.CHARTS], title="Hegram")


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


dropdown = dmc.MultiSelect(
    data=[
        {"value": k, "label": k}
        for k in ["Total", "Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]
    ],
    value=["Total"],
    id="dropdown",
    mb=10,
)

definition_markdown = dcc.Markdown(
    """
    # Select a root in the table!
""",
    id="definition",
)


chart = dmc.BarChart(
    h=450,
    dataKey="Binyan",
    data=[],
    series=[
        {"name": "Qatal", "color": "red.6"},
        {"name": "Yiqtol", "color": "green.6"},
        {"name": "Wayyiqtol", "color": "indigo.6"},
        {"name": "Imperative", "color": "grape.6"},
        {"name": "Infinitive (abslute)", "color": "teal.6"},
        {"name": "Infinitive (construct)", "color": "yellow.6"},
        {"name": "Participle", "color": "pink.6"},
        {"name": "Participle (passive)", "color": "lime.6"},
    ],
    type="stacked",
    barProps={"isAnimationActive": True},
    xAxisLabel="Binyan",
    yAxisLabel="Occurences",
    id="mantine-bargraph",
    className="mantine-barchart",
    px=25,
)


core = html.Div(
    [
        html.Div(
            [
                html.H1("Hegram by ניקולא לינדן"),
                html.P(
                    "An app for hebrew grammar analysis in the Hebrew Bible! Select a verbal root in the table to see the number of its occurences by binyan, you can select multiple root to see the sum of occurences. Use the dropdown menu to add binyan columns to the table, you can then sort the table by number of occurence for your favorite binyan."
                ),
            ],
            className="textbox-container",
        ),
        html.Div(
            children=[
                html.Div([dropdown, table]),
                html.Div(
                    [
                        chart,
                        dmc.RadioGroup(
                            children=dmc.Group(
                                [
                                    dmc.Radio(k, value=k)
                                    for k in [
                                        "Binyan",
                                        "Tense",
                                        "Binyan-Tense",
                                        "Tense-Binyan",
                                    ]
                                ],
                                my=10,
                            ),
                            id="radiogroup",
                            value="Binyan-Tense",
                            size="sm",
                            mb=10,
                            px=25,
                        ),
                    ],
                ),
            ],
            className="occurence-grid textbox-container",
        ),
        html.Div([definition_markdown], className="textbox-container"),
    ],
    className="container",
)

app.layout = dmc.MantineProvider(children=[core])
