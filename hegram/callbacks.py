from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
from hegram.definitions import definitions
from hegram.occurences import occurences
from loguru import logger
from hebrew import Hebrew
from typing import Dict, List, Set, Any, Tuple
import plotly.graph_objects as go

DataList = List[Dict[str, Any]]
Data = Dict[str, str | int]


# @callback(Output("mantine-bargraph", "series"), Input("percent-checkbox", "checked"))
# def toggle_percent(checked):
#     if checked:
#         return [
#             {"name": "Frequency", "color": "orange.6"},
#         ]
#     else:
#         return [
#             {"name": "Occurences", "color": "orange.6"},
#         ]


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
def update_binyanim_bar_graph(
    data: DataList, selected_cells: DataList, radio
) -> go.Figure:
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
        return occurences.binyanim_bar_graph(radio)
    roots = set()
    for cell in selected_cells:
        roots |= get_roots_from_cell(data, cell)
    if roots:
        logger.info(roots)
        return occurences.binyanim_bar_graph(radio, list(roots))
    return occurences.binyanim_bar_graph(radio)


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
        Output("table", "tooltip_data"),
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
    logger.info("sort_by={}", sort_by)
    if len(sort_by):
        key = sort_by[0]["column_id"]
        asc = sort_by[0]["direction"] == "asc"
        _df = (
            occurences.rbo_frame()
            .reset_index("Root")
            .sort_values(by=[key], ascending=asc, inplace=False)
            .iloc[page_current * page_size : (page_current + 1) * page_size]
        )
    else:
        _df = (
            occurences.rbo_frame()
            .reset_index("Root")
            .iloc[page_current * page_size : (page_current + 1) * page_size]
        )
    columns = ["Root"]
    if dropdown_values is not None:
        columns += dropdown_values
    tooltip_data = [
        {"Root": {"value": row["Root"], "type": "markdown"}}
        for row in _df.to_dict("records")
    ]
    tooltip_data = []
    for row in _df.to_dict("records"):
        root = Hebrew(row["Root"]).text_only()
        definition = definitions.get(str(root), [["No definition found"]])
        val = f"# {root}\n\n"
        val += "\n\n".join(definition[0])
        tooltip_data.append({"Root": {"value": val, "type": "markdown"}})
    return _df.to_dict("records"), [{"name": c, "id": c} for c in columns], tooltip_data


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
    _df = occurences.rbo_frame()
    return len(_df) // page_size + int((len(_df) % page_size) != 0)
