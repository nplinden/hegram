import dash
import random
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate

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

_HEBREW_INPUT_STYLE = {"fontFamily": '"Ezra SIL", sans-serif', "fontSize": "1.1rem", "direction": "rtl"}

_BG_NEUTRAL   = "#FFFFFF"
_BG_CORRECT   = "#D4EFDF"
_BG_INCORRECT = "#F2D7D5"
_BG_PARTIAL   = "#FCF3CF"

_COLOR_GIVEN   = "#000000"
_COLOR_CORRECT = "#27AE60"
_COLOR_WRONG   = "#A93226"
_COLOR_UNKNOWN = "#AAAAAA"


def _pool(ranges):
    if not ranges:
        return [n for n in NUMBERS if n["arabic"] <= 10]
    result = [n for n in NUMBERS if any(_RANGE_FILTERS[r](n) for r in ranges if r in _RANGE_FILTERS)]
    return result or [n for n in NUMBERS if n["arabic"] <= 10]


def _select_data(pool, key):
    if key == "arabic":
        return [{"value": str(n["arabic"]), "label": str(n["arabic"])} for n in pool]
    return [{"value": n[key], "label": n[key]} for n in pool]


def _zone(label_text, value, color, is_rtl=False, font_size="3rem", border_right=False, border_bottom=False):
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
        [
            dmc.Text(label_text, size="sm", c="dimmed", ta="center", mb=8),
            html.P(value, style=text_style),
        ],
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


def _card(bg, name_val, name_color, arabic_val, arabic_color, numeral_val, numeral_color):
    top = _zone(
        "Nom hébreu", name_val, name_color,
        is_rtl=True, font_size="2.5rem", border_bottom=True,
    )
    arabic = _zone(
        "Numéral arabe", str(arabic_val), arabic_color,
        font_size="3rem", border_right=True,
    )
    numeral = _zone(
        "Numéral hébreu", numeral_val, numeral_color,
        is_rtl=True, font_size="3rem",
    )
    return html.Div(
        [top, html.Div([arabic, numeral], style={"display": "flex"})],
        style={
            "backgroundColor": bg,
            "borderRadius": "16px",
            "border": "1px solid #e0e0e0",
            "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
            "overflow": "hidden",
            "marginBottom": "24px",
            "maxWidth": "400px",
            "marginInline": "auto",
        },
    )


def _neutral_card(number, given_key):
    def slot(key):
        if key == given_key:
            v = str(number[key]) if key == "arabic" else number[key]
            return v, _COLOR_GIVEN
        return "?", _COLOR_UNKNOWN

    name_v, name_c     = slot("name")
    arabic_v, arabic_c = slot("arabic")
    num_v, num_c       = slot("numeral")
    return _card(_BG_NEUTRAL, name_v, name_c, arabic_v, arabic_c, num_v, num_c)


def _result_card(number, given_key, user_answers):
    correct = wrong = 0
    colors = {}
    for k in REPRESENTATIONS:
        if k == given_key:
            colors[k] = _COLOR_GIVEN
            continue
        expected = str(number[k])
        got = str(user_answers.get(k) or "")
        if got == expected:
            colors[k] = _COLOR_CORRECT
            correct += 1
        else:
            colors[k] = _COLOR_WRONG
            wrong += 1

    if wrong == 0:
        bg = _BG_CORRECT
    elif correct == 0:
        bg = _BG_INCORRECT
    else:
        bg = _BG_PARTIAL

    return _card(
        bg,
        number["name"],        colors["name"],
        str(number["arabic"]), colors["arabic"],
        number["numeral"],     colors["numeral"],
    )


layout = dmc.MantineProvider(
    html.Div(
        [
            html.H1("Exercice sur les nombres"),
            html.P(
                "Un nombre s'affiche sous l'une de ses trois formes. "
                "Retrouvez les deux autres. Les formes de 1 à 19 sont au féminin absolu (formes de comptage)."
            ),
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
            dmc.Flex(
                dmc.Button(
                    "Trouver un nombre",
                    id="numbers-generate-btn",
                    color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                ),
                justify="center",
                mb=24,
            ),
            dcc.Store(id="numbers-store", storage_type="session"),
            html.Div(id="numbers-card"),
            html.Div(
                id="numbers-answer-section",
                style={"display": "none", "maxWidth": "400px", "marginInline": "auto"},
                children=[
                    dmc.Flex(
                        [
                            html.Div(
                                id="numbers-select-name-wrapper",
                                children=[
                                    dmc.Text("Nom hébreu", size="sm", c="dimmed", ta="center", mb=4),
                                    dmc.Select(
                                        id="numbers-select-name",
                                        data=[],
                                        value=None,
                                        searchable=True,
                                        styles={"input": _HEBREW_INPUT_STYLE, "option": _HEBREW_INPUT_STYLE},
                                        comboboxProps={"withinPortal": True},
                                    ),
                                ],
                                style={"flex": 1},
                            ),
                            html.Div(
                                id="numbers-select-arabic-wrapper",
                                children=[
                                    dmc.Text("Numéral arabe", size="sm", c="dimmed", ta="center", mb=4),
                                    dmc.Select(
                                        id="numbers-select-arabic",
                                        data=[],
                                        value=None,
                                        searchable=True,
                                        comboboxProps={"withinPortal": True},
                                    ),
                                ],
                                style={"flex": 1},
                            ),
                            html.Div(
                                id="numbers-select-numeral-wrapper",
                                children=[
                                    dmc.Text("Numéral hébreu", size="sm", c="dimmed", ta="center", mb=4),
                                    dmc.Select(
                                        id="numbers-select-numeral",
                                        data=[],
                                        value=None,
                                        searchable=True,
                                        styles={"input": _HEBREW_INPUT_STYLE, "option": _HEBREW_INPUT_STYLE},
                                        comboboxProps={"withinPortal": True},
                                    ),
                                ],
                                style={"flex": 1},
                            ),
                        ],
                        direction={"base": "column", "sm": "row"},
                        gap="lg",
                        mb=16,
                    ),
                    dmc.Flex(
                        dmc.Button(
                            "Vérifier",
                            id="numbers-check-btn",
                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                        ),
                        justify="center",
                        mb=16,
                    ),
                ],
            ),
        ],
        className="container",
    )
)


@callback(
    Output("numbers-card", "children"),
    Output("numbers-select-name-wrapper", "style"),
    Output("numbers-select-arabic-wrapper", "style"),
    Output("numbers-select-numeral-wrapper", "style"),
    Output("numbers-select-name", "data"),
    Output("numbers-select-arabic", "data"),
    Output("numbers-select-numeral", "data"),
    Output("numbers-select-name", "value"),
    Output("numbers-select-arabic", "value"),
    Output("numbers-select-numeral", "value"),
    Output("numbers-answer-section", "style"),
    Output("numbers-store", "data"),
    Input("numbers-generate-btn", "n_clicks"),
    State("numbers-range-check", "value"),
    prevent_initial_call=True,
)
def generate_number(_, ranges):
    pool = _pool(ranges)
    number = random.choice(pool)
    given_key = random.choice(REPRESENTATIONS)

    shown  = {"flex": 1}
    hidden = {"display": "none"}

    return (
        _neutral_card(number, given_key),
        hidden if given_key == "name"    else shown,
        hidden if given_key == "arabic"  else shown,
        hidden if given_key == "numeral" else shown,
        _select_data(pool, "name"),
        _select_data(pool, "arabic"),
        _select_data(pool, "numeral"),
        None, None, None,
        {"display": "block"},
        {"number": number, "given_key": given_key},
    )


@callback(
    Output("numbers-card", "children", allow_duplicate=True),
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
    return _result_card(
        store["number"],
        store["given_key"],
        {"name": name_val, "arabic": arabic_val, "numeral": numeral_val},
    )
