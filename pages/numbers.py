import dash
import random
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path="/exercises/numbers")

# Feminine absolute forms (default counting forms) for 1–19; invariable for 20+
NUMBERS = [
    {"arabic": 1,   "name": "אַחַת",               "numeral": "א׳"},
    {"arabic": 2,   "name": "שְׁתַּיִם",            "numeral": "ב׳"},
    {"arabic": 3,   "name": "שָׁלֹשׁ",              "numeral": "ג׳"},
    {"arabic": 4,   "name": "אַרְבַּע",             "numeral": "ד׳"},
    {"arabic": 5,   "name": "חָמֵשׁ",               "numeral": "ה׳"},
    {"arabic": 6,   "name": "שֵׁשׁ",                "numeral": "ו׳"},
    {"arabic": 7,   "name": "שֶׁבַע",               "numeral": "ז׳"},
    {"arabic": 8,   "name": "שְׁמֹנֶה",             "numeral": "ח׳"},
    {"arabic": 9,   "name": "תֵּשַׁע",              "numeral": "ט׳"},
    {"arabic": 10,  "name": "עֶשֶׂר",               "numeral": "י׳"},
    {"arabic": 11,  "name": "אַחַת עֶשְׂרֵה",       "numeral": "י״א"},
    {"arabic": 12,  "name": "שְׁתֵּים עֶשְׂרֵה",    "numeral": "י״ב"},
    {"arabic": 13,  "name": "שְׁלֹשׁ עֶשְׂרֵה",     "numeral": "י״ג"},
    {"arabic": 14,  "name": "אַרְבַּע עֶשְׂרֵה",    "numeral": "י״ד"},
    {"arabic": 15,  "name": "חָמֵשׁ עֶשְׂרֵה",      "numeral": "ט״ו"},
    {"arabic": 16,  "name": "שֵׁשׁ עֶשְׂרֵה",       "numeral": "ט״ז"},
    {"arabic": 17,  "name": "שְׁבַע עֶשְׂרֵה",      "numeral": "י״ז"},
    {"arabic": 18,  "name": "שְׁמֹנֶה עֶשְׂרֵה",    "numeral": "י״ח"},
    {"arabic": 19,  "name": "תְּשַׁע עֶשְׂרֵה",     "numeral": "י״ט"},
    {"arabic": 20,  "name": "עֶשְׂרִים",           "numeral": "כ׳"},
    {"arabic": 30,  "name": "שְׁלֹשִׁים",          "numeral": "ל׳"},
    {"arabic": 40,  "name": "אַרְבָּעִים",         "numeral": "מ׳"},
    {"arabic": 50,  "name": "חֲמִשִּׁים",          "numeral": "נ׳"},
    {"arabic": 60,  "name": "שִׁשִּׁים",           "numeral": "ס׳"},
    {"arabic": 70,  "name": "שִׁבְעִים",           "numeral": "ע׳"},
    {"arabic": 80,  "name": "שְׁמֹנִים",           "numeral": "פ׳"},
    {"arabic": 90,  "name": "תִּשְׁעִים",          "numeral": "צ׳"},
    {"arabic": 100, "name": "מֵאָה",              "numeral": "ק׳"},
    {"arabic": 200, "name": "מָאתַיִם",           "numeral": "ר׳"},
    {"arabic": 300, "name": "שְׁלֹשׁ מֵאֹות",     "numeral": "ש׳"},
    {"arabic": 400, "name": "אַרְבַּע מֵאֹות",    "numeral": "ת׳"},
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

_HEBREW_STYLE = {"fontFamily": "\"Ezra SIL\", sans-serif", "fontSize": "1.1rem", "direction": "rtl"}


def _pool(ranges):
    if not ranges:
        return [n for n in NUMBERS if n["arabic"] <= 10]
    result = [n for n in NUMBERS if any(_RANGE_FILTERS[r](n) for r in ranges if r in _RANGE_FILTERS)]
    return result or [n for n in NUMBERS if n["arabic"] <= 10]


def _options(pool, key):
    if key == "arabic":
        return [{"value": str(n["arabic"]), "label": str(n["arabic"])} for n in pool]
    return [{"value": n[key], "label": n[key]} for n in pool]


def _question_card(given_key, given_value):
    is_hebrew = given_key in ("name", "numeral")
    text_style = {
        "fontFamily": "\"Ezra SIL\", sans-serif",
        "fontSize": "3.5rem",
        "textAlign": "center",
        "lineHeight": "1.2",
        **({"direction": "rtl"} if is_hebrew else {}),
    }
    return dmc.Card(
        [
            dmc.Text(LABELS[given_key], size="sm", c="dimmed", ta="center", mb=4),
            html.P(str(given_value), style=text_style),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"maxWidth": "280px", "margin": "0 auto", "padding": "16px"},
        mb=20,
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
                mb=20,
            ),
            dcc.Store(id="numbers-store", storage_type="session"),
            html.Div(id="numbers-question-div"),
            html.Div(
                id="numbers-answer-div",
                style={"display": "none"},
                children=[
                    dmc.Flex(
                        [
                            html.Div(
                                [
                                    dmc.Text(
                                        id="numbers-answer-label-0",
                                        size="sm",
                                        c="dimmed",
                                        ta="center",
                                        mb=4,
                                    ),
                                    dmc.Select(
                                        id="numbers-answer-select-0",
                                        data=[],
                                        value=None,
                                        searchable=True,
                                        styles={"input": _HEBREW_STYLE, "option": _HEBREW_STYLE},
                                        comboboxProps={"withinPortal": True},
                                    ),
                                ],
                                style={"flex": 1},
                            ),
                            html.Div(
                                [
                                    dmc.Text(
                                        id="numbers-answer-label-1",
                                        size="sm",
                                        c="dimmed",
                                        ta="center",
                                        mb=4,
                                    ),
                                    dmc.Select(
                                        id="numbers-answer-select-1",
                                        data=[],
                                        value=None,
                                        searchable=True,
                                        styles={"input": _HEBREW_STYLE, "option": _HEBREW_STYLE},
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
            dmc.Alert(
                "",
                id="numbers-result",
                style={"display": "none"},
                styles={
                    "title": {"fontFamily": "\"Ezra SIL\", sans-serif", "fontSize": "1.4rem", "direction": "rtl"},
                    "message": {"fontSize": "1rem"},
                },
            ),
        ],
        className="container",
    )
)


@callback(
    Output("numbers-question-div", "children"),
    Output("numbers-answer-div", "style"),
    Output("numbers-answer-label-0", "children"),
    Output("numbers-answer-select-0", "data"),
    Output("numbers-answer-select-0", "value"),
    Output("numbers-answer-label-1", "children"),
    Output("numbers-answer-select-1", "data"),
    Output("numbers-answer-select-1", "value"),
    Output("numbers-store", "data"),
    Output("numbers-result", "style", allow_duplicate=True),
    Input("numbers-generate-btn", "n_clicks"),
    State("numbers-range-check", "value"),
    prevent_initial_call=True,
)
def generate_number(_, ranges):
    pool = _pool(ranges)
    number = random.choice(pool)
    given_key = random.choice(REPRESENTATIONS)
    answer_keys = [k for k in REPRESENTATIONS if k != given_key]

    return (
        _question_card(given_key, number[given_key]),
        {"display": "block"},
        LABELS[answer_keys[0]],
        _options(pool, answer_keys[0]),
        None,
        LABELS[answer_keys[1]],
        _options(pool, answer_keys[1]),
        None,
        {"number": number, "answer_keys": answer_keys},
        {"display": "none"},
    )


@callback(
    Output("numbers-result", "children"),
    Output("numbers-result", "title"),
    Output("numbers-result", "color"),
    Output("numbers-result", "style", allow_duplicate=True),
    Input("numbers-check-btn", "n_clicks"),
    State("numbers-store", "data"),
    State("numbers-answer-select-0", "value"),
    State("numbers-answer-select-1", "value"),
    prevent_initial_call=True,
)
def check_answer(_, store, val0, val1):
    if not store:
        raise PreventUpdate

    number = store["number"]
    k0, k1 = store["answer_keys"]

    correct0 = str(number[k0])
    correct1 = str(number[k1])
    ok0 = (val0 or "") == correct0
    ok1 = (val1 or "") == correct1

    title = f"{number['arabic']}  ·  {number['name']}  ·  {number['numeral']}"
    lines = []
    for label, val, correct, ok in [
        (LABELS[k0], val0, correct0, ok0),
        (LABELS[k1], val1, correct1, ok1),
    ]:
        mark = "✓" if ok else f"✗  →  {correct}"
        lines.append(html.P(f"{label} : {val or '—'}  {mark}"))

    color = "green" if (ok0 and ok1) else "red"
    return lines, title, color, {"display": "block"}
