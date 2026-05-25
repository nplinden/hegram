import dash_mantine_components as dmc
from dash import dcc, Input, Output, callback, html
from dash_iconify import DashIconify

_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "overflow": "hidden",
    "backgroundColor": "#FFFFFF",
}

_HEADER_STYLE = {
    "padding": "12px 20px",
    "backgroundColor": "#F8F9FA",
    "borderBottom": "1px solid #e0e0e0",
}

_ROW_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "padding": "6px 20px",
    "gap": "16px",
    "borderBottom": "1px solid rgba(0,0,0,0.05)",
}

_HEB_STYLE = {
    "fontFamily": '"Ezra SIL", sans-serif',
    "fontSize": "1.8rem",
    "direction": "rtl",
    "textAlign": "right",
    "margin": 0,
    "flex": 1,
}


def _conj_card(title, pairs):
    rows = [
        html.Div(
            [
                dmc.Text(person, size="sm", c="dimmed", style={"minWidth": "40px", "flexShrink": 0}),
                html.P(form, style=_HEB_STYLE),
            ],
            style=_ROW_STYLE,
        )
        for person, form in pairs
    ]
    return html.Div(
        [html.Div(dmc.Text(title, fw=600, size="md"), style=_HEADER_STYLE), *rows],
        style=_CARD_STYLE,
    )


def _single_card(title, form):
    return html.Div(
        [
            html.Div(dmc.Text(title, fw=600, size="md"), style=_HEADER_STYLE),
            html.Div(
                html.P(form, style={**_HEB_STYLE, "fontSize": "2.5rem", "textAlign": "center"}),
                style={"padding": "20px", "textAlign": "center"},
            ),
        ],
        style=_CARD_STYLE,
    )


def _grid(*children, mb=16):
    return dmc.SimpleGrid(
        cols={"base": 1, "sm": 2},
        spacing="lg",
        mb=mb,
        children=list(children),
    )


def make_page(page_id, title, root, asset, accompli, inaccompli,
              imperatif=None, participe=None, absolu=None, construit=None):
    rows = []

    if absolu is not None and construit is not None:
        rows.append(_grid(_single_card("Infinitif absolu", absolu),
                          _single_card("Infinitif construit", construit)))
    elif absolu is not None:
        rows.append(html.Div(_single_card("Infinitif absolu", absolu), style={"marginBottom": "16px"}))
    elif construit is not None:
        rows.append(html.Div(_single_card("Infinitif construit", construit), style={"marginBottom": "16px"}))

    rows.append(_grid(_conj_card("Accompli", accompli), _conj_card("Inaccompli", inaccompli)))

    if imperatif is not None and participe is not None:
        rows.append(_grid(_conj_card("Impératif", imperatif),
                          _conj_card("Participe présent", participe), mb=0))
    elif participe is not None:
        rows.append(_conj_card("Participe présent", participe))
    elif imperatif is not None:
        rows.append(_conj_card("Impératif", imperatif))

    layout = dmc.MantineProvider(
        html.Div(
            [
                dcc.Download(id=f"download-{page_id}"),
                dmc.Flex(
                    [
                        html.Div(style={"width": "36px"}),
                        html.H1(title, style={"margin": 0, "flex": 1, "textAlign": "center"}),
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:download", width=20),
                            id=f"btn-{page_id}",
                            variant="subtle",
                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                            size="lg",
                        ),
                    ],
                    align="center",
                    mb=16,
                ),
                html.Div(_single_card("Racine", root), style={"marginBottom": "16px"}),
                *rows,
            ],
            className="container",
            style={"maxWidth": "860px", "marginInline": "auto"},
        )
    )

    @callback(
        Output(f"download-{page_id}", "data"),
        Input(f"btn-{page_id}", "n_clicks"),
        prevent_initial_call=True,
    )
    def _download(_):
        return dcc.send_file(asset)

    return layout
