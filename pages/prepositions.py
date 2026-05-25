import dash
import pandas as pd
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash_iconify import DashIconify

dash.register_page(__name__, path="/exercises/prepositions")

flexion = pd.read_csv("data/prepositions.csv")

_BG_NEUTRAL  = "#FFFFFF"
_BG_REVEALED = "#D4EFDF"

_COLOR_HEBREW = "#000000"
_COLOR_FRENCH = "#27AE60"
_COLOR_HIDDEN = "#AAAAAA"

_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "overflow": "hidden",
    "maxWidth": "400px",
    "marginInline": "auto",
    "marginBottom": "24px",
}


def _zone(label, value, color, is_rtl=False, font_size="3rem", border_bottom=False):
    text_style = {
        "fontFamily": '"Ezra SIL", sans-serif',
        "fontSize": font_size,
        "textAlign": "center",
        "color": color,
        "margin": "0",
        "lineHeight": "1.3",
    }
    if is_rtl:
        text_style["direction"] = "rtl"
    border = {"borderBottom": "1px solid rgba(0,0,0,0.1)"} if border_bottom else {}
    min_h = "140px" if font_size == "3rem" else "120px"
    return html.Div(
        [dmc.Text(label, size="sm", c="dimmed", ta="center", mb=8), html.P(value, style=text_style)],
        style={"padding": "24px 16px", "display": "flex", "flexDirection": "column",
               "justifyContent": "center", "alignItems": "center", "minHeight": min_h, **border},
    )


def _neutral_card(row):
    return html.Div(
        [
            _zone("Hébreu", row["hebrew"], _COLOR_HEBREW, is_rtl=True, border_bottom=True),
            _zone("Français", "?", _COLOR_HIDDEN, font_size="2rem"),
        ],
        style={**_CARD_STYLE, "backgroundColor": _BG_NEUTRAL},
    )


def _revealed_card(row):
    return html.Div(
        [
            _zone("Hébreu", row["hebrew"], _COLOR_HEBREW, is_rtl=True, border_bottom=True),
            _zone("Français", row["french"], _COLOR_FRENCH, font_size="2rem"),
        ],
        style={**_CARD_STYLE, "backgroundColor": _BG_REVEALED},
    )


def _sample(with_suffix):
    if not with_suffix:
        return flexion[flexion["person"] == "base"].sample(n=1).iloc[0].to_dict()
    return flexion.sample(n=1).iloc[0].to_dict()


layout = dmc.MantineProvider(
    html.Div(
        [
            dcc.Store(id="prep-store", storage_type="session"),
            dcc.Interval(id="prep-init", interval=1, max_intervals=1),
            dmc.Modal(
                id="prep-intro-modal",
                opened=False,
                title="Exercice sur les prépositions",
                children=[
                    html.P(
                        "Une préposition hébraïque s'affiche. "
                        "Retrouvez sa traduction française. "
                        "Activez les suffixes dans les paramètres pour inclure les formes avec pronoms suffixes."
                    ),
                ],
            ),
            dmc.Modal(
                id="prep-settings-modal",
                opened=False,
                title="Paramètres",
                children=[
                    dmc.Checkbox(
                        id="prep-suffix-check",
                        label="Inclure les suffixes",
                        checked=False,
                        mb=8,
                    ),
                ],
            ),
            html.Div(
                dmc.Flex(
                    [
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:info", width=20),
                            id="prep-intro-btn",
                            variant="subtle",
                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                            size="lg",
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:settings", width=20),
                            id="prep-settings-btn",
                            variant="subtle",
                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                            size="lg",
                        ),
                    ],
                    justify="flex-end",
                    align="center",
                    gap="xs",
                ),
                style={"maxWidth": "400px", "marginInline": "auto", "marginBottom": "4px"},
            ),
            html.Div(id="prep-card"),
            dmc.Button(
                "Voir la solution",
                id="prep-action-btn",
                color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                fullWidth=True,
                radius="xl",
                size="md",
                style={"maxWidth": "400px", "marginInline": "auto", "display": "block", "marginBottom": "24px"},
            ),
        ],
        className="container",
    )
)


@callback(
    Output("prep-intro-modal", "opened"),
    Input("prep-intro-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_intro_modal(_):
    return True


@callback(
    Output("prep-settings-modal", "opened"),
    Input("prep-settings-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_settings_modal(_):
    return True


def _generate(with_suffix):
    row = _sample(with_suffix)
    return _neutral_card(row), "Voir la solution", {"row": row, "answered": False}


@callback(
    Output("prep-card", "children"),
    Output("prep-action-btn", "children"),
    Output("prep-store", "data"),
    Input("prep-init", "n_intervals"),
    State("prep-suffix-check", "checked"),
    prevent_initial_call=True,
)
def initial_generate(_, with_suffix):
    return _generate(with_suffix)


@callback(
    Output("prep-card", "children", allow_duplicate=True),
    Output("prep-action-btn", "children", allow_duplicate=True),
    Output("prep-store", "data", allow_duplicate=True),
    Input("prep-action-btn", "n_clicks"),
    State("prep-store", "data"),
    State("prep-suffix-check", "checked"),
    prevent_initial_call=True,
)
def handle_action(_, store, with_suffix):
    if store is None or store.get("answered"):
        return _generate(with_suffix)
    row = store["row"]
    return _revealed_card(row), "Nouvelle préposition", {**store, "answered": True}
