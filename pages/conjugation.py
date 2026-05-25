import dash
import dash_mantine_components as dmc
import json as _json
from dash import html, no_update
import polars as pl
from bs4 import BeautifulSoup
from dash import callback, Input, Output, State, dcc, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from hegram.mechon_mamre import verse_to_url, en_to_fr_books

from hegram.data import dropdown_data, en_to_fr, answer_data, roots_data
from hegram.definitions import definitions
from hegram.utils import convert_html_to_dash, htmlify
from hebrew import Hebrew

_book_index = _json.load(open("json/index.json", encoding="utf-8"))
_book_cache: dict = {}


def _get_chapters(json_file: str) -> list:
    if json_file not in _book_cache:
        with open(f"json/{json_file}", encoding="utf-8") as f:
            _book_cache[json_file] = _json.load(f)["chapters"]
    return _book_cache[json_file]

COMMON_BINYANIM = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]

_ANSWER_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "overflow": "hidden",
    "backgroundColor": "#FFFFFF",
    "maxWidth": "640px",
    "marginInline": "auto",
    "marginBottom": "24px",
}

_VERSE_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "backgroundColor": "#FFFFFF",
    "maxWidth": "640px",
    "marginInline": "auto",
    "padding": "24px",
    "marginBottom": "16px",
}

dash.register_page(__name__, path="/exercises/conjugation")


def build_verse(verse_id, word_id):
    # print(verse_id, word_id)
    df = pl.scan_parquet("data/verses.parquet").filter(pl.col("id") == verse_id).collect().to_dicts()[0]
    word_df = pl.scan_parquet("data/words.parquet").filter(pl.col("id") == word_id).collect()
    word = BeautifulSoup(word_df.to_dicts()[0]["html"], features="html.parser").find("span").string

    html = BeautifulSoup(df["html"], features="html.parser")
    html.find("span", string=word)["class"].append("hl")
    html.find("div")["class"] = ["fullverse"]
    return convert_html_to_dash(str(html))


def build_word(word_id):
    word_df = pl.scan_parquet("data/words.parquet").filter(pl.col("id") == word_id).collect().to_dicts()[0]
    html = BeautifulSoup(word_df["html"], features="html.parser")
    html.find("div")["class"] = ["singleword"]
    return convert_html_to_dash(str(html))


def passage(verse_id: int):
    df = pl.scan_parquet("data/verses.parquet").filter(pl.col("id") == verse_id).collect().to_dicts()[0]
    book = en_to_fr_books[df["book"]]
    chapter, verse = df["chapter"], df["verse"]
    name = f"{book} {chapter}:{verse}"
    url = verse_to_url(book, int(chapter))
    return html.A(
        children=[name],
        href=url,
        target="_blank",
        style={"color": "black", "font-style": "italic"},
    )


def french_passage(verse_id: int):
    df = pl.scan_parquet("data/verses.parquet").filter(pl.col("id") == verse_id).collect().to_dicts()[0]
    book, chapter, verse = df["book"], df["chapter"], df["verse"]
    entry = _book_index[book]
    chapters = _get_chapters(entry["json_file"])
    fr_ch = chapters[chapter - 1 + entry["chapter_offset"]]
    ch_map = entry.get("verse_maps", {}).get(str(chapter))
    if ch_map and verse - 1 < len(ch_map):
        fr_v_idx = ch_map[verse - 1]
    else:
        fr_v_idx = min(verse - 1, len(fr_ch) - 1)
    text = fr_ch[fr_v_idx]
    return html.P([passage(verse_id), f" : {text}"])


@callback(
    Output("clause-div", "children"),
    Output("word-div", "children"),
    Output("solution-storage", "data"),
    Output("verse-card", "style"),
    Output("conj-detail-modal", "children"),
    Output("notification", "children"),
    Output("answer-card", "style"),
    Output("frenchverse-div", "children"),
    Output("frenchverse-div", "style"),
    Output("conj-action-btn", "children"),
    Output("answer-dropdowns", "style"),
    Output("answer-results", "children"),
    Output("answer-results", "style"),
    Output("root-answer", "value"),
    Output("binyan-answer", "value"),
    Output("tense-answer", "value"),
    Output("person-answer", "value"),
    Input("conj-action-btn", "n_clicks"),
    State("conjugation-roots-dropdown", "value"),
    State("conjugation-book-dropdown", "value"),
    State("conjugation-binyan-dropdown", "value"),
    State("conjugation-tense-dropdown", "value"),
    State("conjugation-person-dropdown", "value"),
    State("conjugation-gender-dropdown", "value"),
    State("conjugation-number-dropdown", "value"),
    State("solution-storage", "data"),
    State("root-answer", "value"),
    State("binyan-answer", "value"),
    State("tense-answer", "value"),
    State("person-answer", "value"),
    prevent_initial_call=True,
)
def handle_action(_, roots, book, binyanim, tenses, persons, genders, numbers,
                  store, root_answer, binyan_answer, tense_answer, person_answer):
    if store is None or store.get("answered"):
        df = pl.scan_parquet("data/conjugation.parquet")
        filtered = df.filter(
            pl.when(bool(book)).then(pl.col("Book").is_in(book)).otherwise(pl.lit(True))
            & pl.when(bool(binyanim)).then(pl.col("Binyan").is_in(binyanim)).otherwise(pl.lit(True))
            & pl.when(bool(tenses)).then(pl.col("Tense").is_in(tenses)).otherwise(pl.lit(True))
            & pl.when(bool(persons)).then(pl.col("Person").is_in(persons)).otherwise(pl.lit(True))
            & pl.when(bool(genders)).then(pl.col("Gender").is_in(genders)).otherwise(pl.lit(True))
            & pl.when(bool(numbers)).then(pl.col("Number").is_in(numbers)).otherwise(pl.lit(True))
            & pl.when(bool(roots)).then(pl.col("Root").is_in(roots)).otherwise(pl.lit(True))
        ).collect()
        if filtered.is_empty():
            return (
                no_update, no_update, no_update, no_update,
                no_update,
                dmc.Notification(
                    title="Erreur",
                    action="show",
                    message="Aucun verbe ne satisfait ces filtres !",
                    icon=DashIconify(
                        icon="material-symbols:error-outline-rounded",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                    ),
                ),
                no_update, no_update, no_update, no_update,
                no_update, no_update, no_update,
                no_update, no_update, no_update, no_update,
            )
        sample = filtered.sample(n=1).to_dicts()[0]
        verse, word = sample["VerseId"], sample["WordId"]
        return (
            build_verse(verse, word),
            build_word(word),
            sample,
            {**_VERSE_CARD_STYLE, "display": "block"},
            no_update,
            no_update,
            {**_ANSWER_CARD_STYLE, "display": "block"},
            no_update,
            {"display": "none"},
            "Vérifier",
            {"display": "flex", "flexDirection": "column", "gap": "12px"},
            [],
            {"display": "none"},
            None, None, None, None,
        )

    root = store["Root"]
    tense = en_to_fr["Tense"][store["Tense"]]
    binyan = store["Binyan"]
    number = {"Singular": "S", "Plural": "P"}.get(store["Number"], "")
    person = {"1": "1", "2": "2", "3": "3"}.get(store.get("Person", ""), "")
    gender = {"M": "M", "F": "F"}.get(store.get("Gender", ""), "")
    rest = f"{person}{gender}{number}"

    root_nodiacr = Hebrew(root).text_only()
    definition = definitions.get(str(root_nodiacr), [["No definition found"]])[0]
    html_parts = ["<div>"]
    for d in definition:
        html_parts.append(htmlify(d))
    html_parts.append("</div>")

    solution = f"{binyan} {tense} {rest}"
    chart = dmc.BarChart(
        h=450,
        dataKey="Binyan",
        data=barchart(root),
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
        id="solution-bargraph",
        className="mantine-barchart",
        px=25,
    )

    root_ok = root_answer == root
    binyan_ok = binyan_answer == binyan
    tense_ok = tense_answer == store["Tense"]
    person_ok = (person_answer or "") == rest
    n_correct = sum([root_ok, binyan_ok, tense_ok, person_ok])

    if n_correct == 4:
        bg, alert_color = "#D4EFDF", "green"
    elif n_correct == 0:
        bg, alert_color = "#FADBD8", "red"
    else:
        bg, alert_color = "#FFF9C4", "yellow"

    tense_fr = en_to_fr["Tense"][store["Tense"]]
    tense_guess_fr = en_to_fr["Tense"].get(tense_answer, tense_answer) if tense_answer else "—"

    answer_panel = [
        _answer_row(0, root, root_answer or "—", root_ok),
        _answer_row(1, binyan, binyan_answer or "—", binyan_ok),
        _answer_row(2, tense_fr, tense_guess_fr, tense_ok),
        _answer_row(3, rest or "—", person_answer or "—", person_ok),
    ]

    detail_modal_content = [
        html.P(
            root,
            style={"fontFamily": '"Ezra SIL", sans-serif', "fontSize": "3rem",
                   "direction": "rtl", "textAlign": "center", "margin": "0 0 8px"},
        ),
        convert_html_to_dash("\n".join(html_parts)),
        chart,
    ]

    return (
        no_update,
        no_update,
        {**store, "answered": True},
        no_update,
        detail_modal_content,
        no_update,
        {**_ANSWER_CARD_STYLE, "display": "block", "backgroundColor": bg},
        french_passage(store["VerseId"]),
        {"display": "block", "borderTop": "1px solid rgba(0,0,0,0.1)", "marginTop": "16px", "paddingTop": "16px"},
        "Trouver un verbe",
        {"display": "none"},
        answer_panel,
        {"display": "flex", "flexDirection": "column", "gap": "12px"},
        no_update, no_update, no_update, no_update,
    )


def barchart(root):
    df = pl.scan_parquet("data/conjugation.parquet").filter(
        (pl.col("Root") == root) & (pl.col("Binyan").is_in(COMMON_BINYANIM))
    )
    df = (
        df.select(["Binyan", "Tense"])
        .collect()
        .to_struct(name="Struct")
        .value_counts()
        .unnest("Struct")
        .sort("count", descending=True)
    )
    return df.pivot(["Tense"], index="Binyan", values="count").fill_null(0).to_dicts()


def data_from_list(items):
    return [{"value": k, "label": k} for k in items]


def get_root_select_data():
    roots = pl.scan_parquet("data/conjugation.parquet").select(["Root"]).unique().sort(["Root"]).collect().to_series()
    data = [{"label": v, "value": v} for v in roots]
    return data


_ROOT_DATA = get_root_select_data()


def _answer_row(index, correct, guess, is_correct):
    if index == 0:
        icon = dmc.ActionIcon(
            DashIconify(icon="material-symbols:help-outline", width=14),
            id={"type": "answer-help-btn", "index": index},
            variant="subtle",
            size="xs",
            color="gray",
        )
    else:
        icon = None
    if is_correct:
        text_el = dmc.Text(correct or "—", c="green.7", fw=600, size="lg")
    else:
        text_el = html.Div(
            [
                dmc.Text(correct or "—", c="green.7", fw=600, size="lg"),
                dmc.Text(guess or "—", c="red.6", size="lg",
                         style={"textDecoration": "line-through"}),
            ],
            style={"display": "flex", "gap": "8px", "alignItems": "center"},
        )
    children = [text_el] + ([icon] if icon else [])
    return html.Div(
        children,
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "gap": "8px",
            "border": "1px solid rgba(0,0,0,0.12)",
            "borderRadius": "4px",
            "padding": "8px 12px",
            "backgroundColor": "rgba(255,255,255,0.5)",
        },
    )


root_select = dmc.MultiSelect(
    label="Racines autorisées",
    data=roots_data,
    value=[],
    id="conjugation-roots-dropdown",
    mb=10,
)

book_select = dmc.MultiSelect(
    label="Livres autorisés",
    data=dropdown_data["Book"],
    value=[],
    id="conjugation-book-dropdown",
    mb=10,
)

binyan_select = dmc.MultiSelect(
    label="Binyanim autorisés",
    data=dropdown_data["Binyan"],
    value=[],
    id="conjugation-binyan-dropdown",
    mb=10,
)

tense_select = dmc.MultiSelect(
    label="Temps autorisés",
    data=dropdown_data["Tense"],
    value=[],
    id="conjugation-tense-dropdown",
    mb=10,
)

person_select = dmc.MultiSelect(
    label="Personnes autorisées",
    data=dropdown_data["Person"],
    value=[],
    id="conjugation-person-dropdown",
    mb=10,
)

gender_select = dmc.MultiSelect(
    label="Genres autorisés",
    data=dropdown_data["Gender"],
    value=[],
    id="conjugation-gender-dropdown",
    mb=10,
)

number_select = dmc.MultiSelect(
    label="Nombres autorisées",
    data=dropdown_data["Number"],
    value=[],
    id="conjugation-number-dropdown",
    mb=10,
)

solution_head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Racine"),
            dmc.TableTh("Binyan"),
            dmc.TableTh("Temps"),
            dmc.TableTh("Personne"),
            dmc.TableTh("Genre"),
            dmc.TableTh("Nombre"),
        ]
    )
)

solution_body = dmc.TableTbody(
    [
        dmc.TableTr(
            [
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
                dmc.TableTd(""),
            ]
        )
    ],
    id="solution-body",
)

def layout():
    return dmc.MantineProvider(
        dash.html.Div(
            children=[
                dcc.Store(id="solution-storage", storage_type="memory"),
            dmc.Modal(
                id="conj-detail-modal",
                opened=False,
                size="xl",
                children=[],
            ),
            dmc.Modal(
                id="conj-intro-modal",
                opened=False,
                title="Exercice de conjugaison",
                children=[
                    html.P(
                        "Une application d'exercice à la conjugaison en hébreu biblique. Cliquez sur \"Trouver un verbe\" pour choisir aléatoirement une forme verbale dans le corpus biblique. Essayez d'analyser la conjugaison de ce verbe ! Le verset correspondant est également fourni pour plus de contexte."
                    ),
                    html.P(
                        'L\'icône "Paramètres" permet de restreindre le choix des formes verbales.'
                    ),
                ],
            ),
            dmc.Modal(
                id="conj-settings-modal",
                opened=False,
                title="Paramètres",
                children=[
                    root_select,
                    book_select,
                    binyan_select,
                    tense_select,
                    person_select,
                    gender_select,
                    number_select,
                ],
            ),
            dmc.Flex(
                [
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:info", width=20),
                        id="conj-intro-btn",
                        variant="subtle",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                        size="lg",
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:settings", width=20),
                        id="conj-settings-btn",
                        variant="subtle",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                        size="lg",
                    ),
                ],
                justify="flex-end",
                align="center",
                gap="xs",
                mb=4,
            ),
            dmc.Flex(
                dmc.Button(
                    "Trouver un verbe",
                    id="conj-action-btn",
                    color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                    radius="xl",
                    size="md",
                ),
                justify="center",
                mb=16,
            ),
            html.Div(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(children=[], id="word-div"),
                            ],
                            style={
                                "flex": 1,
                                "borderRight": "1px solid rgba(0,0,0,0.1)",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "padding": "24px 16px",
                                "minHeight": "200px",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dmc.Select(placeholder="Racine", value=None, data=_ROOT_DATA, searchable=True, id="root-answer"),
                                        dmc.Select(placeholder="Binyan", value=None, data=dropdown_data["Binyan"], id="binyan-answer"),
                                        dmc.Select(placeholder="Temps", value=None, data=dropdown_data["Tense"], id="tense-answer"),
                                        dmc.Select(placeholder="Personne", value=None, data=answer_data, id="person-answer"),
                                    ],
                                    id="answer-dropdowns",
                                    style={"display": "flex", "flexDirection": "column", "gap": "12px"},
                                ),
                                html.Div(
                                    [],
                                    id="answer-results",
                                    style={"display": "none"},
                                ),
                            ],
                            id="answer-panel",
                            style={
                                "flex": 1,
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "12px",
                                "padding": "24px 16px",
                                "justifyContent": "center",
                            },
                        ),
                    ],
                    style={"display": "flex"},
                ),
                id="answer-card",
                style={**_ANSWER_CARD_STYLE, "display": "none"},
            ),
            html.Div(
                [
                    dmc.Flex(children=[], id="clause-div", className="fullverse"),
                    html.Div(
                        [],
                        id="frenchverse-div",
                        className="frenchverse",
                        style={"display": "none", "borderTop": "1px solid rgba(0,0,0,0.1)", "marginTop": "16px", "paddingTop": "16px"},
                    ),
                ],
                id="verse-card",
                style={**_VERSE_CARD_STYLE, "display": "none"},
            ),
        ],
        className="container",
    )
    )


@callback(
    Output("conj-intro-modal", "opened"),
    Input("conj-intro-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_intro_modal(_):
    return True


@callback(
    Output("conj-settings-modal", "opened"),
    Input("conj-settings-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_settings_modal(_):
    return True


@callback(
    Output("conj-detail-modal", "opened"),
    Input({"type": "answer-help-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_detail_modal(n_clicks_list):
    if any(n for n in n_clicks_list if n):
        return True
    raise PreventUpdate
