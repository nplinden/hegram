from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
from hegram.build import df, definitions
from hegram.utils import binyanim_freq
from loguru import logger
from hebrew import Hebrew
from typing import Dict, List, Set, Any, Tuple

DataList = List[Dict[str, Any]]
Data = Dict[str, str | int]

@callback(
    Output("binyanim_root", "figure", allow_duplicate=True),
    [Input("table", "data"), 
     Input("table", "selected_cells"),
     Input("table", "page_current")], 
    prevent_initial_call=True
)
def table_select(data: DataList, 
                 selected_cells: DataList, 
                 page_current: int) -> "go.Figure":
    """Trigger figure update on cell selection

    Args:
        data (DataList): The data contained in the table
        selected_cells (DataList): The list of selected cells
        page_current (int): The current table page

    Raises:
        PreventUpdate: In case no cell is selected

    Returns:
        go.Figure: The resulting bar graph figure
    """
    logger.info("Triggering table_select callback")
    if selected_cells is None:
        raise PreventUpdate
    logger.info("data={}", data)
    logger.info("selected_cells={}", selected_cells)
    logger.info("page_current={}", page_current)
    roots = set()
    for cell in selected_cells:
        roots |= get_roots_from_cell(data, cell)
    if roots:
        logger.info(roots)
        return binyanim_freq(df, roots=list(roots))
    
    roots = list(df.index)
    return binyanim_freq(df, roots=roots)

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
    if column_id == "Racine":
        return set([data[row][column_id]])
    elif column_id == "Classe":
        classname = data[row][column_id]
        _df = df[df.Classe == classname]
        return set(_df.index)
    else:
        return set()

@callback(
        [Output("table", "data"), 
         Output("table", "columns"),
         Output("table", "tooltip_data")],
        Input("table", "page_current"),
        Input("table", "page_size"),
        Input("table", "sort_by"),
        Input("dropdown", "value")
)
def update_table(page_current: int, page_size: int, sort_by: str, dropdown_values: List[str]) -> Tuple[DataList, DataList, DataList]:
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
        _df = (df.reset_index(names=["Racine"])
               .sort_values(by=[key], ascending=asc, inplace=False)
               .iloc[page_current*page_size:(page_current+1)*page_size])
    else:
        _df = (df.reset_index(names=["Racine"])
               .iloc[page_current*page_size:(page_current+1)*page_size])
    columns = ["Rank", "Racine", "Classe"]
    if dropdown_values is not None:
        columns += dropdown_values
    tooltip_data = [{"Racine": {"value": row["Racine"], "type": "markdown"}} 
                    for row in _df.to_dict("records")]
    tooltip_data = []
    for row in _df.to_dict("records"):
        print(list(Hebrew(row["Racine"]).graphemes))
        root = Hebrew(row["Racine"]).text_only()
        definition = definitions.get(str(root), [["No definition found"]])
        logger.info(definitions["אמר"])
        val = f"**{root}**\n\n"
        val += "\n\n".join(definition[0])
        tooltip_data.append(
            {"Racine": {"value": val, "type": "markdown"}}
        )
    return _df.to_dict("records"), [{"name": c, "id": c} for c in columns], tooltip_data


@callback(
        Output("table", "page_count"),
        Input("table", "page_size")
)
def update_table_page_number(page_size: int) -> int:
    """Compute the total number of pages need to display the entire
    dataframe

    Args:
        page_size (int): The size of a single page

    Returns:
        int: The total number of pages
    """
    return len(df) // page_size + int((len(df) % page_size) != 0)
