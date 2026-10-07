import dash
from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from hegram.data import COMMON_BINYANIM, TENSE_SERIES
from hegram.definitions import definitions
from hegram.stats import ROOT_BINYAN_COUNTS, binyan_tense_counts
from hegram.utils import htmlify, convert_html_to_dash
from loguru import logger
from hebrew import Hebrew
from typing import Dict, List, Set, Any, Tuple

import dash_mantine_components as dmc
from dash import html, dash_table

dash.register_page(__name__, path="/statistics")

DataList = List[Dict[str, Any]]
Data = Dict[str, str | int]


@callback(
    Output("mantine-bargraph", "data"),
    [
        Input("table", "data"),
        Input("table", "selected_cells"),
    ],
)
def update_binyanim_bar_graph(data: DataList, selected_cells: DataList):
    logger.info("Triggering table_select callback")
    if selected_cells is None:
        return binyan_tense_counts()
    roots = set()
    for cell in selected_cells:
        roots |= get_roots_from_cell(data, cell)
    if roots:
        logger.info(roots)
        return binyan_tense_counts(list(roots))
    return binyan_tense_counts()


def get_roots_from_cell(data: DataList, cell: Data) -> Set[str]:
    """Get the list of roots from a selected cell

    Args:
        data (DataList): The data contained in the table
        cell (Data): The selected cell

    Returns:
        Set[str]: The set of verb roots
    """
    column_id = cell["column_id"]
    row = cell["row"]
    if column_id == "Root":
        return set([data[row][column_id]])
    else:
        return set()


@callback(
    [
        Output("table", "data"),
        Output("table", "columns"),
    ],
    Input("table", "page_current"),
    Input("table", "page_size"),
    Input("table", "sort_by"),
    Input("dropdown", "value"),
)
def update_table(
    page_current: int, page_size: int, sort_by: str, dropdown_values: List[str]
) -> Tuple[DataList, DataList, DataList, str]:
    """Update the table page on the value of the dropdown widget.

    Args:
        page_current (int): The current page of the table
        page_size (int): The size of a table page
        sort_by (str): The columns name by which to sort the table
        dropdown_values (List[str]): The list of additionnal columns from
                                     the dropdown menu

    Returns:
        Tuple[DataList, DataList, DataList]: The table data, list of columns, and tooltip data
    """
    df = ROOT_BINYAN_COUNTS
    if len(sort_by):
        key = sort_by[0]["column_id"]
        asc = sort_by[0]["direction"] == "asc"
        df = df.sort(key, descending=not asc)

    if dropdown_values is None:
        df = df.select(["Root"])
    else:
        df = df.select(["Root"] + dropdown_values)

    rows = df.to_dicts()[page_current * page_size : (page_current + 1) * page_size]
    return rows, [{"name": c, "id": c} for c in df.columns]


_DEFINITION_CARD_STYLE = {
    "maxWidth": "640px",
    "marginInline": "auto",
    "border": "1px solid rgba(0,0,0,0.12)",
    "borderRadius": "8px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "padding": "24px",
    "display": "none",
}


@callback(
    Output("definition-card", "children"),
    Output("definition-card", "style"),
    Input("table", "active_cell"),
    Input("table", "data"),
)
def update_definition(active_cell: Data, data: DataList):
    logger.info("active_cell={}", active_cell)
    if active_cell is None:
        raise PreventUpdate
    if active_cell["column_id"] != "Root":
        raise PreventUpdate

    root = Hebrew(list(get_roots_from_cell(data, active_cell))[0]).text_only()
    logger.info("root={}", root)
    definition = definitions.get(str(root), [["No definition found"]])[0]
    html_parts = ["<div>"]
    for d in definition:
        html_parts.append(htmlify(d))
    html_parts.append("</div>")

    children = [
        html.P(
            str(root),
            style={
                "fontFamily": "var(--font)",
                "fontSize": "3rem",
                "direction": "rtl",
                "textAlign": "center",
                "margin": "0 0 12px",
            },
        ),
        convert_html_to_dash("\n".join(html_parts)),
    ]
    return children, {**_DEFINITION_CARD_STYLE, "display": "block"}


@callback(Output("table", "page_count"), Input("table", "page_size"))
def update_table_page_number(page_size: int) -> int:
    """Compute the total number of pages need to display the entire
    dataframe

    Args:
        page_size (int): The size of a single page

    Returns:
        int: The total number of pages
    """
    nroot = len(ROOT_BINYAN_COUNTS)
    return nroot // page_size + int((nroot % page_size) != 0)


table = dash_table.DataTable(
    id="table",
    columns=[{"name": c, "id": c} for c in ["Rank", "Root", "Class", "Total"]],
    page_current=0,
    page_size=12,
    page_count=100,
    page_action="custom",
    style_cell={"fontSize": 20, "fontFamily": "var(--font)", "fontVariantNumeric": "tabular-nums"},
    style_cell_conditional=[
        {
            "if": {"column_id": "Root"},
            "font-family": "var(--font)",
            "fontSize": 20,
        },
        {
            "if": {"column_id": "Class"},
            "font-family": "var(--font)",
            "fontSize": 20,
        },
    ],
    sort_action="custom",
    sort_mode="single",
    sort_by=[],
    tooltip_duration=None,
)

dropdown = dmc.MultiSelect(
    data=[{"value": k, "label": k} for k in ["Total"] + COMMON_BINYANIM],
    value=["Total"],
    id="dropdown",
    mb=10,
)

chart = dmc.BarChart(
    h=560,
    dataKey="Binyan",
    data=[],
    series=TENSE_SERIES,
    type="stacked",
    barProps={"isAnimationActive": True},
    xAxisLabel="Binyan",
    orientation="vertical",
    id="mantine-bargraph",
    className="mantine-barchart",
    px=25,
)


@callback(
    Output("stat-intro-modal", "opened"),
    Input("stat-intro-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_stat_intro_modal(_):
    return True


layout = html.Div(
    [
        dmc.Modal(
            id="stat-intro-modal",
            opened=False,
            size="xl",
            title="Statistiques sur les racines verbales",
            children=[
                html.P(
                    "Vous trouverez ici un aperçu du nombre d'occurrences de chaque racine verbale dans la Bible hébraïque, avec une ventilation selon les binyanim et les temps. Cette page comporte trois volets :"
                ),
                dmc.List(
                    [
                        dmc.ListItem(
                            "Un tableau de toutes les racines verbales existantes et de leur nombre total d'occurrences. Sélectionnez un binyan dans le menu déroulant ajouter la colonne correspondante au tableau. En cliquant sur les flèches dans l'en-tête de la colonne. Vous pouvez trier le tableau par nombre d'occurrences pour le binôme correspondant."
                        ),
                        dmc.ListItem(
                            "Le diagramme à barres montre la répartition des occurrences de binyan et de temps dans la Bible hébraïque. Par défaut, il montre une agrégation de toutes les occurrences de racines verbales. En sélectionnant une ou plusieurs racines dans le tableau, vous pouvez restreindre les racines prises en compte dans le graphique."
                        ),
                        dmc.ListItem(
                            [
                                "Lorsqu'une racine est sélectionnée dans le tableau, une section de définition apparaît sous le graphique. Les définitions sont tirées du ",
                                html.A(
                                    "dépôt GitHub openscriptures",
                                    href="https://github.com/openscriptures/strongs/",
                                    className="link",
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        ),
        dmc.Flex(
            [
                dmc.ActionIcon(
                    DashIconify(icon="material-symbols:info", width=20),
                    id="stat-intro-btn",
                    variant="subtle",
                    color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                    size="lg",
                ),
            ],
            justify="flex-end",
            align="center",
            className="container",
        ),
        html.Div(
            children=[
                html.Div([dropdown, table]),
                html.Div(
                    [
                        chart,
                    ],
                ),
            ],
            className="occurrence-grid container",
        ),
        html.Div(
            [],
            id="definition-card",
            style=_DEFINITION_CARD_STYLE,
            className="container",
        ),
    ],
)
