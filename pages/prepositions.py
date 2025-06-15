import dash
from dash import callback, Input, Output, State, dcc
from dash import html, no_update
import dash_mantine_components as dmc
from random import choice
from dash.dash_table import DataTable
from pages.datatable_style import style
import pandas as pd

dash.register_page(__name__, path="/exercises/prepositions")

prep_he_to_fr = {
    "בּ": "Dans",
    "כְּ": "Comme",
    "לְ": "Pour",
    "מִן": "De",
    "עִם": "Avec",
    "עַל": "Sur",
    "אֶל": "Vers",
    "אֵת": "Avec/Accusatif",
    "הִנֵּה": "Voici",
    "בֵּין": "Entre",
    "אַיִן": "N'est pas",
}
prep_fr_to_he = {v: k for k, v in prep_he_to_fr.items()}
prepositions = list(prep_he_to_fr.keys())

flexion = pd.read_csv("data/prepositions.csv")

print(flexion)


def build_table(hebrew, french):
    return DataTable(
        data=[
            {"Hébreu": hebrew, "Français": french},
        ],
        columns=[
            {"name": "Hébreu", "id": "Hébreu"},
            {"name": "Français", "id": "Français"},
        ],
        **style,
    )


layout = dmc.MantineProvider(
    children=[
        html.H1("Exercice sur les prépositions"),
        html.P("Une application simple pour se tester sur la connaissance des prépositions !"),
        dmc.Flex(
            [
                dmc.Checkbox(
                    labelPosition="right",
                    label="Inclure les suffixes",
                    variant="filled",
                    size="sm",
                    radius="sm",
                    id="suffix-check",
                ),
            ],
            direction={"base": "column", "sm": "row"},
            gap={"base": "sm", "sm": "lg"},
            justify={"sm": "center"},
            mb=10,
        ),
        dmc.Flex(
            [
                dmc.Button("Nouvelle préposition", id="preposition-btn", color=dmc.DEFAULT_THEME["colors"]["dark"][6]),
                dmc.Button("Solution", id="solution-btn", color=dmc.DEFAULT_THEME["colors"]["dark"][6]),
            ],
            direction={"base": "column", "sm": "row"},
            gap={"base": "sm", "sm": "lg"},
            justify={"sm": "center"},
            mb=10,
        ),
        dcc.Store(id="solution-store", storage_type="session"),
        html.Div(
            children=[
                DataTable(
                    data=[
                        {"Hébreu": "", "Français": ""},
                    ],
                    columns=[
                        {"name": "Hébreu", "id": "Hébreu"},
                        {"name": "Français", "id": "Français"},
                    ],
                    **style,
                )
            ],
            id="preposition-div",
            style={"textAlign": "center"},
        ),
    ]
)


@callback(
    Output("preposition-div", "children", allow_duplicate=True),
    Output("solution-store", "data"),
    Input("preposition-btn", "n_clicks"),
    State("suffix-check", "checked"),
    prevent_initial_call=True,
)
def generate_preposition(clicked, with_suffix):
    if not with_suffix:
        row = flexion[flexion["person"] == "base"].sample(n=1).iloc[0]
    else:
        row = flexion.sample(n=1).iloc[0]
    return build_table(row["hebrew"], ""), [row.to_dict()]


@callback(
    Output("preposition-div", "children", allow_duplicate=True),
    Input("solution-btn", "n_clicks"),
    State("solution-store", "data"),
    prevent_initial_call=True,
)
def show_solution(clicked, data):
    return build_table(data[0]["hebrew"], data[0]["french"])
