import dash
from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
from hegram.definitions import definitions
from loguru import logger
from hebrew import Hebrew
from typing import Dict, List, Set, Any, Tuple
import plotly.graph_objects as go
import polars as pl

import dash_mantine_components as dmc
from dash import html, dcc, dash_table

dash.register_page(__name__, path="/statistics")

DataList = List[Dict[str, Any]]
Data = Dict[str, str | int]

COMMON_BINYANIM = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]


def binyanim_barchart(radio, roots=None):
    df = pl.scan_parquet("data/conjugation.parquet").filter(
        pl.when(bool(roots)).then(pl.col("Root").is_in(roots)).otherwise(pl.lit(True))
        & pl.col("Binyan").is_in(COMMON_BINYANIM)
    )
    if radio in ["Binyan-Tense", "Tense-Binyan"]:
        df = (
            df.select(["Binyan", "Tense"])
            .collect()
            .to_struct(name="Struct")
            .value_counts()
            .unnest("Struct")
            .sort("count", descending=True)
        )
        if radio == "Binyan-Tense":
            return df.pivot(["Tense"], index="Binyan", values="count").fill_null(0).to_dicts()
        else:
            return df.pivot(["Binyan"], index="Tense", values="count").fill_null(0).to_dicts()
    elif radio == "Binyan":
        df = df.select(["Binyan"])
    elif radio == "Tense":
        df = df.select(["Tense"])
    return df.collect().to_series().value_counts(name="Occurences").sort("Occurences", descending=True).to_dicts()


@callback(
    Output("mantine-bargraph", "series"),
    Output("mantine-bargraph", "dataKey"),
    Output("mantine-bargraph", "xAxisLabel"),
    Input("radiogroup", "value"),
)
def update_barchart_series(radio):
    if radio == "Binyan-Tense":
        return (
            [
                {"name": "Qatal", "color": "red.6"},
                {"name": "Yiqtol", "color": "green.6"},
                {"name": "Wayyiqtol", "color": "indigo.6"},
                {"name": "Imperative", "color": "grape.6"},
                {"name": "Infinitive (abslute)", "color": "teal.6"},
                {"name": "Infinitive (construct)", "color": "yellow.6"},
                {"name": "Participle", "color": "pink.6"},
                {"name": "Participle (passive)", "color": "lime.6"},
            ],
            "Binyan",
            "Binyan",
        )
    elif radio == "Tense-Binyan":
        return (
            [
                {"name": "Paal", "color": "red.6"},
                {"name": "Piel", "color": "green.6"},
                {"name": "Pual", "color": "indigo.6"},
                {"name": "Nifal", "color": "grape.6"},
                {"name": "Hofal", "color": "teal.6"},
                {"name": "Hitpael", "color": "yellow.6"},
                {"name": "Hifil", "color": "yellow.6"},
            ],
            "Tense",
            "Tense",
        )
    elif radio == "Binyan":
        return [{"name": "Occurences", "color": "green.6"}], "Binyan", "Binyan"
    elif radio == "Tense":
        return [{"name": "Occurences", "color": "green.6"}], "Tense", "Tense"


@callback(
    Output("mantine-bargraph", "data"),
    [
        Input("table", "data"),
        Input("table", "selected_cells"),
        Input("radiogroup", "value"),
    ],
)
def update_binyanim_bar_graph(data: DataList, selected_cells: DataList, radio) -> go.Figure:
    """Trigger figure update on cell selection

    Args:
        data (DataList): The data contained in the table
        selected_cells (DataList): The list of selected cells

    Raises:
        PreventUpdate: In case no cell is selected

    Returns:
        go.Figure: The resulting bar graph figure
    """
    logger.info("Triggering table_select callback")
    if selected_cells is None:
        return binyanim_barchart(radio)
    roots = set()
    for cell in selected_cells:
        roots |= get_roots_from_cell(data, cell)
    if roots:
        logger.info(roots)
        return binyanim_barchart(radio, list(roots))
    return binyanim_barchart(radio)


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
    df = (
        pl.scan_parquet("data/conjugation.parquet")
        .select(["Root", "Binyan"])
        .collect()
        .to_struct("Struct")
        .value_counts()
        .unnest("Struct")
        .pivot("Binyan", index="Root", values="count")
        .fill_null(0)
        .select(["Root"] + COMMON_BINYANIM)
        .with_columns(Total=pl.sum_horizontal(COMMON_BINYANIM))
        .sort("Total", descending=True)
        .filter(pl.col("Total") > 0)
    )
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


@callback(
    Output("definition", "children"),
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
    definition = definitions.get(str(root), [["No definition found"]])

    val = f"# {root}\n\n"
    val += "\n\n".join(definition[0])
    return val


@callback(Output("table", "page_count"), Input("table", "page_size"))
def update_table_page_number(page_size: int) -> int:
    """Compute the total number of pages need to display the entire
    dataframe

    Args:
        page_size (int): The size of a single page

    Returns:
        int: The total number of pages
    """
    df = (
        pl.scan_parquet("data/conjugation.parquet")
        .select(["Root", "Binyan"])
        .collect()
        .to_struct("Struct")
        .value_counts()
        .unnest("Struct")
        .pivot("Binyan", index="Root", values="count")
        .fill_null(0)
        .select(["Root"] + COMMON_BINYANIM)
        .with_columns(Total=pl.sum_horizontal(COMMON_BINYANIM))
        .sort("Total", descending=True)
        .filter(pl.col("Total") > 0)
    )
    nroot = len(df)
    return nroot // page_size + int((nroot % page_size) != 0)


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
    data=[{"value": k, "label": k} for k in ["Total", "Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]],
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
    orientation="vertical",
    id="mantine-bargraph",
    className="mantine-barchart",
    px=25,
)


layout = dmc.MantineProvider(
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Statistiques sur les racines verbales"),
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
                    className="container",
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
                    className="occurrence-grid container",
                ),
                html.Div([definition_markdown], className="container"),
            ],
        )
    ]
)
