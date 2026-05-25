import dash
import random
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

dash.register_page(__name__, path="/exercises/numbers")

# Feminine absolute forms (default counting forms) for 1–19; invariable for 20+
NUMBERS = [
    {"arabic": 1,   "name": "אַחַת",               "numeral": "א"},
    {"arabic": 2,   "name": "שְׁתַּיִם",            "numeral": "ב"},
    {"arabic": 3,   "name": "שָׁלֹשׁ",              "numeral": "ג"},
    {"arabic": 4,   "name": "אַרְבַּע",             "numeral": "ד"},
    {"arabic": 5,   "name": "חָמֵשׁ",               "numeral": "ה"},
    {"arabic": 6,   "name": "שֵׁשׁ",                "numeral": "ו"},
    {"arabic": 7,   "name": "שֶׁבַע",               "numeral": "ז"},
    {"arabic": 8,   "name": "שְׁמֹנֶה",             "numeral": "ח"},
    {"arabic": 9,   "name": "תֵּשַׁע",              "numeral": "ט"},
    {"arabic": 10,  "name": "עֶשֶׂר",               "numeral": "י"},
    {"arabic": 11,  "name": "אַחַת עֶשְׂרֵה",       "numeral": "יא"},
    {"arabic": 12,  "name": "שְׁתֵּים עֶשְׂרֵה",    "numeral": "יב"},
    {"arabic": 13,  "name": "שְׁלֹשׁ עֶשְׂרֵה",     "numeral": "יג"},
    {"arabic": 14,  "name": "אַרְבַּע עֶשְׂרֵה",    "numeral": "יד"},
    {"arabic": 15,  "name": "חָמֵשׁ עֶשְׂרֵה",      "numeral": "טו"},
    {"arabic": 16,  "name": "שֵׁשׁ עֶשְׂרֵה",       "numeral": "טז"},
    {"arabic": 17,  "name": "שְׁבַע עֶשְׂרֵה",      "numeral": "יז"},
    {"arabic": 18,  "name": "שְׁמֹנֶה עֶשְׂרֵה",    "numeral": "יח"},
    {"arabic": 19,  "name": "תְּשַׁע עֶשְׂרֵה",     "numeral": "יט"},
    {"arabic": 20,  "name": "עֶשְׂרִים",           "numeral": "כ"},
    {"arabic": 30,  "name": "שְׁלֹשִׁים",          "numeral": "ל"},
    {"arabic": 40,  "name": "אַרְבָּעִים",         "numeral": "מ"},
    {"arabic": 50,  "name": "חֲמִשִּׁים",          "numeral": "נ"},
    {"arabic": 60,  "name": "שִׁשִּׁים",           "numeral": "ס"},
    {"arabic": 70,  "name": "שִׁבְעִים",           "numeral": "ע"},
    {"arabic": 80,  "name": "שְׁמֹנִים",           "numeral": "פ"},
    {"arabic": 90,  "name": "תִּשְׁעִים",          "numeral": "צ"},
    {"arabic": 100, "name": "מֵאָה",              "numeral": "ק"},
    {"arabic": 200, "name": "מָאתַיִם",           "numeral": "ר"},
    {"arabic": 300, "name": "שְׁלֹשׁ מֵאֹות",     "numeral": "ש"},
    {"arabic": 400, "name": "אַרְבַּע מֵאֹות",    "numeral": "ת"},
]

_RANGE_FILTERS = {
    "1-10":    lambda n: 1   <= n["arabic"] <= 10,
    "11-19":   lambda n: 11  <= n["arabic"] <= 19,
    "20-90":   lambda n: 20  <= n["arabic"] <= 90,
    "100-400": lambda n: 100 <= n["arabic"] <= 400,
}

REPRESENTATIONS = ["arabic", "name", "numeral"]

LABELS = {
    "arabic":  "Numéral arabe",
    "name":    "Nom hébreu",
    "numeral": "Numéral hébreu",
}

_HEBREW_SELECT_STYLES = {
    "input":  {"fontFamily": '"Ezra SIL", sans-serif', "fontSize": "1rem", "direction": "rtl"},
    "option": {"fontFamily": '"Ezra SIL", sans-serif', "direction": "rtl"},
}

_BG_NEUTRAL   = "#FFFFFF"
_BG_CORRECT   = "#D4EFDF"
_BG_INCORRECT = "#F2D7D5"
_BG_PARTIAL   = "#FCF3CF"

_COLOR_GIVEN   = "#000000"
_COLOR_CORRECT = "#27AE60"
_COLOR_WRONG   = "#A93226"

_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "overflow": "hidden",
    "maxWidth": "400px",
    "marginInline": "auto",
    "marginBottom": "24px",
}


def _pool(ranges):
    if not ranges:
        return [n for n in NUMBERS if n["arabic"] <= 10]
    result = [n for n in NUMBERS if any(_RANGE_FILTERS[r](n) for r in ranges if r in _RANGE_FILTERS)]
    return result or [n for n in NUMBERS if n["arabic"] <= 10]


def _select_data(pool, key):
    if key == "arabic":
        return [{"value": str(n["arabic"]), "label": str(n["arabic"])} for n in pool]
    return [{"value": n[key], "label": n[key]} for n in pool]


def _text_zone(label, value, color, is_rtl=False, font_size="3rem", border_right=False, border_bottom=False):
    borders = {}
    if border_right:
        borders["borderRight"] = "1px solid rgba(0,0,0,0.1)"
    if border_bottom:
        borders["borderBottom"] = "1px solid rgba(0,0,0,0.1)"
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
    return html.Div(
        [dmc.Text(label, size="sm", c="dimmed", ta="center", mb=8), html.P(value, style=text_style)],
        style={
            "padding": "24px 16px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "flex": 1,
            **borders,
        },
    )


def _select_zone(label, select_component, border_right=False, border_bottom=False):
    borders = {}
    if border_right:
        borders["borderRight"] = "1px solid rgba(0,0,0,0.1)"
    if border_bottom:
        borders["borderBottom"] = "1px solid rgba(0,0,0,0.1)"
    return html.Div(
        [dmc.Text(label, size="sm", c="dimmed", ta="center", mb=8), select_component],
        style={
            "padding": "16px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "stretch",
            "flex": 1,
            **borders,
        },
    )


def _make_select(key, pool):
    return dmc.Select(
        id=f"numbers-select-{key}",
        data=_select_data(pool, key),
        value=None,
        searchable=True,
        styles=_HEBREW_SELECT_STYLES if key in ("name", "numeral") else {},
        comboboxProps={"withinPortal": True},
    )


def _neutral_card(number, given_key, pool):
    def make_zone(key, border_right=False, border_bottom=False):
        label = LABELS[key]
        is_rtl = key in ("name", "numeral")
        font_size = "2.5rem" if key == "name" else "3rem"
        # Always render the select so its ID is always in the DOM.
        # For the given slot, hide it and show the value as text instead.
        select = _make_select(key, pool)
        if key == given_key:
            v = str(number[key]) if key == "arabic" else number[key]
            borders = {}
            if border_right:
                borders["borderRight"] = "1px solid rgba(0,0,0,0.1)"
            if border_bottom:
                borders["borderBottom"] = "1px solid rgba(0,0,0,0.1)"
            text_style = {
                "fontFamily": '"Ezra SIL", sans-serif',
                "fontSize": font_size,
                "textAlign": "center",
                "color": _COLOR_GIVEN,
                "margin": "0",
                "lineHeight": "1.3",
            }
            if is_rtl:
                text_style["direction"] = "rtl"
            return html.Div(
                [
                    dmc.Text(label, size="sm", c="dimmed", ta="center", mb=8),
                    html.P(v, style=text_style),
                    html.Div(select, style={"display": "none"}),
                ],
                style={
                    "padding": "24px 16px", "display": "flex", "flexDirection": "column",
                    "justifyContent": "center", "alignItems": "center", "flex": 1,
                    **borders,
                },
            )
        return _select_zone(label, select,
                            border_right=border_right, border_bottom=border_bottom)

    top    = make_zone("name", border_bottom=True)
    left   = make_zone("arabic", border_right=True)
    right  = make_zone("numeral")
    return html.Div(
        [top, html.Div([left, right], style={"display": "flex"})],
        style={**_CARD_STYLE, "backgroundColor": _BG_NEUTRAL},
    )


def _result_card(number, given_key, user_answers):
    correct = wrong = 0
    colors = {}
    for k in REPRESENTATIONS:
        if k == given_key:
            colors[k] = _COLOR_GIVEN
            continue
        if str(user_answers.get(k) or "") == str(number[k]):
            colors[k] = _COLOR_CORRECT
            correct += 1
        else:
            colors[k] = _COLOR_WRONG
            wrong += 1

    bg = _BG_CORRECT if wrong == 0 else (_BG_INCORRECT if correct == 0 else _BG_PARTIAL)

    top   = _text_zone(LABELS["name"],    number["name"],        colors["name"],    is_rtl=True, font_size="2.5rem", border_bottom=True)
    left  = _text_zone(LABELS["arabic"],  str(number["arabic"]), colors["arabic"],  font_size="3rem", border_right=True)
    right = _text_zone(LABELS["numeral"], number["numeral"],     colors["numeral"], is_rtl=True, font_size="3rem")
    return html.Div(
        [top, html.Div([left, right], style={"display": "flex"})],
        style={**_CARD_STYLE, "backgroundColor": bg},
    )


layout = dmc.MantineProvider(
    html.Div(
        [
            dcc.Store(id="numbers-store", storage_type="session"),
            html.Div(id="numbers-card"),
            dmc.Flex(
                [
                    dmc.Button(
                        "Trouver un nombre",
                        id="numbers-generate-btn",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                    ),
                    html.Div(
                        dmc.Button(
                            "Vérifier",
                            id="numbers-check-btn",
                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                        ),
                        id="numbers-verify-section",
                        style={"display": "none"},
                    ),
                ],
                justify="center",
                gap="md",
                mb=24,
            ),
            dmc.Accordion(
                disableChevronRotation=False,
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(
                                "Introduction",
                                icon=DashIconify(
                                    icon="material-symbols:text-snippet",
                                    color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                                    width=20,
                                ),
                            ),
                            dmc.AccordionPanel(
                                [
                                    html.H1("Exercice sur les nombres"),
                                    html.P(
                                        "Un nombre s'affiche sous l'une de ses trois formes. "
                                        "Retrouvez les deux autres. Les formes de 1 à 19 sont au féminin absolu (formes de comptage)."
                                    ),
                                ]
                            ),
                        ],
                        value="introduction",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(
                                "Paramètres",
                                icon=DashIconify(
                                    icon="material-symbols:settings",
                                    color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                                    width=20,
                                ),
                            ),
                            dmc.AccordionPanel(
                                [
                                    dmc.CheckboxGroup(
                                        id="numbers-range-check",
                                        label="Plages autorisées",
                                        value=["1-10"],
                                        children=dmc.Group(
                                            [
                                                dmc.Checkbox(value="1-10",    label="1–10"),
                                                dmc.Checkbox(value="11-19",   label="11–19"),
                                                dmc.Checkbox(value="20-90",   label="20–90"),
                                                dmc.Checkbox(value="100-400", label="100–400"),
                                            ]
                                        ),
                                        mb=16,
                                    ),
                                    dmc.CheckboxGroup(
                                        id="numbers-hint-type-check",
                                        label="Formes pouvant être données comme indice",
                                        value=["arabic", "name", "numeral"],
                                        children=dmc.Group(
                                            [
                                                dmc.Checkbox(value="arabic",  label="Numéral arabe"),
                                                dmc.Checkbox(value="name",    label="Nom hébreu"),
                                                dmc.Checkbox(value="numeral", label="Numéral hébreu"),
                                            ]
                                        ),
                                        mb=8,
                                    ),
                                ]
                            ),
                        ],
                        value="settings",
                    ),
                ],
                mb=10,
                value="introduction",
                id="numbers-accordion",
            ),
        ],
        className="container",
    )
)


@callback(
    Output("numbers-card", "children"),
    Output("numbers-verify-section", "style"),
    Output("numbers-store", "data"),
    Input("numbers-generate-btn", "n_clicks"),
    State("numbers-range-check", "value"),
    State("numbers-hint-type-check", "value"),
    prevent_initial_call=True,
)
def generate_number(_, ranges, hint_types):
    pool = _pool(ranges)
    number = random.choice(pool)
    allowed_given = [k for k in REPRESENTATIONS if k in (hint_types or REPRESENTATIONS)]
    given_key = random.choice(allowed_given or REPRESENTATIONS)
    return (
        _neutral_card(number, given_key, pool),
        {"display": "block"},
        {"number": number, "given_key": given_key},
    )


@callback(
    Output("numbers-card", "children", allow_duplicate=True),
    Output("numbers-verify-section", "style", allow_duplicate=True),
    Input("numbers-check-btn", "n_clicks"),
    State("numbers-store", "data"),
    State("numbers-select-name", "value"),
    State("numbers-select-arabic", "value"),
    State("numbers-select-numeral", "value"),
    prevent_initial_call=True,
)
def check_answer(_, store, name_val, arabic_val, numeral_val):
    if not store:
        raise PreventUpdate
    return (
        _result_card(
            store["number"],
            store["given_key"],
            {"name": name_val, "arabic": arabic_val, "numeral": numeral_val},
        ),
        {"display": "none"},
    )
