import dash
import dash_mantine_components as dmc
import json as _json
from dash import html, no_update
import polars as pl
from bs4 import BeautifulSoup
from dash import callback, Input, Output, State, dcc, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from loguru import logger
from hegram.books import en_to_fr_books
from hegram.mechon_mamre import verse_to_url

from hegram.data import TENSE_SERIES, answer_data, dropdown_data, en_to_fr
from hegram.definitions import definitions
from hegram.pdf import render_pdf
from hegram.stats import binyan_tense_counts
from hegram.utils import convert_html_to_dash, htmlify
from hegram.verses import build_verse_html, verse_words
from hebrew import Hebrew

_book_index = _json.load(open("json/index.json", encoding="utf-8"))
_book_cache: dict = {}


def _get_chapters(json_file: str) -> list:
    if json_file not in _book_cache:
        with open(f"json/{json_file}", encoding="utf-8") as f:
            _book_cache[json_file] = _json.load(f)["chapters"]
    return _book_cache[json_file]


_ANSWER_CARD_STYLE = {
    "maxWidth": "640px",
    "marginInline": "auto",
    "marginBottom": "24px",
}

_VERSE_CARD_STYLE = {
    "maxWidth": "640px",
    "marginInline": "auto",
    "padding": "24px",
    "marginBottom": "16px",
}

dash.register_page(__name__, path="/exercises/conjugation")


_NO_VERB_MESSAGE = "Aucun verbe ne satisfait ces filtres !"
_NO_QUESTION_COUNT_MESSAGE = "Indiquez un nombre de questions."
_PDF_FAILED_MESSAGE = "La génération du PDF a échoué. Veuillez réessayer."
_NO_QUESTIONNAIRE_MESSAGE = "Téléchargez d'abord le questionnaire."


def _error_notification(message):
    return dmc.Notification(
        title="Erreur",
        action="show",
        message=message,
        icon=DashIconify(
            icon="material-symbols:error-outline-rounded",
            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
        ),
    )


def build_verse(verse_id, word_id):
    verse_row = pl.scan_parquet("data/verses.parquet").filter(pl.col("id") == verse_id).collect().to_dicts()[0]
    return convert_html_to_dash(build_verse_html(verse_row, verse_words([verse_row]), word_id))


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


def filter_conjugations(roots, books, binyanim, tenses, persons, genders, numbers) -> pl.DataFrame:
    """Verb occurrences matching the settings filters. An empty or unset filter allows every value."""
    filters = {
        "Root": roots,
        "Book": books,
        "Binyan": binyanim,
        "Tense": tenses,
        "Person": persons,
        "Gender": genders,
        "Number": numbers,
    }
    conditions = [pl.col(column).is_in(values) for column, values in filters.items() if values]
    df = pl.scan_parquet("data/conjugation.parquet")
    if conditions:
        df = df.filter(conditions)
    return df.collect()


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
def handle_action(
    _,
    roots,
    book,
    binyanim,
    tenses,
    persons,
    genders,
    numbers,
    store,
    root_answer,
    binyan_answer,
    tense_answer,
    person_answer,
):
    if store is None or store.get("answered"):
        filtered = filter_conjugations(roots, book, binyanim, tenses, persons, genders, numbers)
        if filtered.is_empty():
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                _error_notification(_NO_VERB_MESSAGE),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
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
            None,
            None,
            None,
            None,
        )

    root = store["Root"]
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

    chart = dmc.BarChart(
        h=450,
        dataKey="Binyan",
        data=binyan_tense_counts([root]),
        series=TENSE_SERIES,
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
        bg = "#D4EFDF"
    elif n_correct == 0:
        bg = "#FADBD8"
    else:
        bg = "#FFF9C4"

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
            style={
                "fontFamily": '"Ezra SIL", sans-serif',
                "fontSize": "3rem",
                "direction": "rtl",
                "textAlign": "center",
                "margin": "0 0 8px",
            },
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
        no_update,
        no_update,
        no_update,
        no_update,
    )


def get_root_select_data():
    roots = pl.scan_parquet("data/conjugation.parquet").select(["Root"]).unique().sort(["Root"]).collect().to_series()
    data = [{"label": v, "value": v} for v in roots]
    return data


_ROOT_DATA = get_root_select_data()


def _roots_by_frequency() -> list[str]:
    df = (
        pl.scan_parquet("data/conjugation.parquet")
        .group_by("Root")
        .agg(pl.len().alias("count"))
        .sort(["count", "Root"], descending=[True, False])
        .collect()
    )
    return df["Root"].to_list()


_ROOTS_BY_FREQ = _roots_by_frequency()
_N_ROOTS = len(_ROOTS_BY_FREQ)


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
                dmc.Text(guess or "—", c="red.6", size="lg", style={"textDecoration": "line-through"}),
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


root_freq_slider = dmc.Box(
    [
        dmc.Text("Fréquence des racines", size="sm", fw=500, mb=4),
        dmc.Group(
            [
                dmc.NumberInput(
                    id="conjugation-roots-rank-from",
                    label="Du rang",
                    description="1 = le plus fréquent",
                    min=1,
                    max=_N_ROOTS,
                    step=1,
                    value=1,
                    style={"flex": 1},
                ),
                dmc.NumberInput(
                    id="conjugation-roots-rank-to",
                    label="Au rang",
                    description=f"max = {_N_ROOTS}",
                    min=1,
                    max=_N_ROOTS,
                    step=1,
                    value=_N_ROOTS,
                    style={"flex": 1},
                ),
            ],
            grow=True,
            align="flex-start",
        ),
    ],
    mb=10,
)

root_select = dmc.MultiSelect(
    label="Racines autorisées",
    data=[{"label": root, "value": root} for root in _ROOTS_BY_FREQ],
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


def layout():
    return dash.html.Div(
        children=[
            dcc.Store(id="solution-storage", storage_type="memory"),
            dcc.Store(id="conj-pdf-samples", storage_type="memory"),
            dcc.Download(id="conj-pdf-download"),
            dcc.Download(id="conj-correction-download"),
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
                    html.P('L\'icône "Paramètres" permet de restreindre le choix des formes verbales.'),
                ],
            ),
            dmc.Modal(
                id="conj-settings-modal",
                opened=False,
                title="Paramètres",
                children=[
                    root_freq_slider,
                    root_select,
                    book_select,
                    binyan_select,
                    tense_select,
                    person_select,
                    gender_select,
                    number_select,
                    dmc.Divider(label="Fiche d'exercice PDF", labelPosition="left", my=12),
                    dmc.Text(
                        "Générez une fiche imprimable de verbes tirés au hasard selon les filtres ci-dessus. "
                        "Le corrigé correspond à la dernière fiche téléchargée.",
                        size="sm",
                        c="dimmed",
                        mb=8,
                    ),
                    dmc.NumberInput(
                        id="conj-pdf-n-questions",
                        label="Nombre de questions",
                        min=1,
                        max=50,
                        step=1,
                        value=10,
                        w=160,
                        mb=12,
                    ),
                    dmc.Group(
                        [
                            dmc.Button(
                                "Questionnaire",
                                id="conj-pdf-btn",
                                leftSection=DashIconify(icon="material-symbols:download", width=18),
                                variant="outline",
                                color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                            ),
                            dmc.Button(
                                "Corrigé",
                                id="conj-correction-btn",
                                disabled=True,
                                leftSection=DashIconify(icon="material-symbols:download", width=18),
                                variant="light",
                                color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                            ),
                        ],
                        grow=True,
                    ),
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
            dmc.Button(
                "Trouver un verbe",
                id="conj-action-btn",
                color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                radius="xl",
                size="md",
                fullWidth=True,
                style={"maxWidth": "640px", "marginInline": "auto", "display": "block", "marginBottom": "16px"},
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
                                        dmc.Select(
                                            placeholder="Racine",
                                            value=None,
                                            data=_ROOT_DATA,
                                            searchable=True,
                                            id="root-answer",
                                        ),
                                        dmc.Select(
                                            placeholder="Binyan",
                                            value=None,
                                            data=dropdown_data["Binyan"],
                                            id="binyan-answer",
                                        ),
                                        dmc.Select(
                                            placeholder="Temps",
                                            value=None,
                                            data=dropdown_data["Tense"],
                                            id="tense-answer",
                                        ),
                                        dmc.Select(
                                            placeholder="Personne", value=None, data=answer_data, id="person-answer"
                                        ),
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
                className="card",
                style={**_ANSWER_CARD_STYLE, "display": "none"},
            ),
            html.Div(
                [
                    dmc.Flex(children=[], id="clause-div", className="fullverse"),
                    html.Div(
                        [],
                        id="frenchverse-div",
                        className="frenchverse",
                        style={
                            "display": "none",
                            "borderTop": "1px solid rgba(0,0,0,0.1)",
                            "marginTop": "16px",
                            "paddingTop": "16px",
                        },
                    ),
                ],
                id="verse-card",
                className="card",
                style={**_VERSE_CARD_STYLE, "display": "none"},
            ),
        ],
        className="container",
    )


@callback(
    Output("conj-intro-modal", "opened"),
    Input("conj-intro-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_intro_modal(_):
    return True


@callback(
    Output("conjugation-roots-dropdown", "value"),
    Input("conjugation-roots-rank-from", "value"),
    Input("conjugation-roots-rank-to", "value"),
    prevent_initial_call=True,
)
def inputs_to_root_select(lo, hi):
    if lo is None or hi is None:
        return no_update
    lo = max(1, int(lo))
    hi = min(_N_ROOTS, int(hi))
    if lo == 1 and hi == _N_ROOTS:
        return []
    return _ROOTS_BY_FREQ[lo - 1 : hi]


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


@callback(
    Output("conj-pdf-download", "data"),
    Output("conj-pdf-samples", "data"),
    Output("notification", "children", allow_duplicate=True),
    Input("conj-pdf-btn", "n_clicks"),
    State("conj-pdf-n-questions", "value"),
    State("conjugation-roots-dropdown", "value"),
    State("conjugation-book-dropdown", "value"),
    State("conjugation-binyan-dropdown", "value"),
    State("conjugation-tense-dropdown", "value"),
    State("conjugation-person-dropdown", "value"),
    State("conjugation-gender-dropdown", "value"),
    State("conjugation-number-dropdown", "value"),
    prevent_initial_call=True,
)
def generate_pdf(n_clicks, n_questions, roots, book, binyanim, tenses, persons, genders, numbers):
    # The notification output lives outside this page, so Dash ignores prevent_initial_call
    # and fires this callback when the page loads: only act on an actual click.
    if not n_clicks:
        raise PreventUpdate
    if not n_questions:
        return no_update, no_update, _error_notification(_NO_QUESTION_COUNT_MESSAGE)
    try:
        filtered = filter_conjugations(roots, book, binyanim, tenses, persons, genders, numbers)
        if filtered.is_empty():
            return no_update, no_update, _error_notification(_NO_VERB_MESSAGE)
        k = min(int(n_questions), len(filtered))
        samples = filtered.sample(n=k).to_dicts()
        pdf_bytes = render_pdf(samples, with_answers=False)
        return dcc.send_bytes(pdf_bytes, filename="questionnaire_conjugaison.pdf"), samples, no_update
    except Exception:
        logger.exception("PDF generation failed")
        return no_update, no_update, _error_notification(_PDF_FAILED_MESSAGE)


@callback(
    Output("conj-correction-btn", "disabled"),
    Input("conj-pdf-samples", "data"),
)
def enable_correction_btn(samples):
    # The answer key is built from the questionnaire's verbs, so it is only available
    # once a questionnaire has been downloaded.
    return not samples


@callback(
    Output("conj-correction-download", "data"),
    Output("notification", "children", allow_duplicate=True),
    Input("conj-correction-btn", "n_clicks"),
    State("conj-pdf-samples", "data"),
    prevent_initial_call=True,
)
def generate_correction_pdf(n_clicks, samples):
    # See generate_pdf: only act on an actual click.
    if not n_clicks:
        raise PreventUpdate
    if not samples:
        return no_update, _error_notification(_NO_QUESTIONNAIRE_MESSAGE)
    try:
        pdf_bytes = render_pdf(samples, with_answers=True)
        return dcc.send_bytes(pdf_bytes, filename="corrige_conjugaison.pdf"), no_update
    except Exception:
        logger.exception("Correction PDF generation failed")
        return no_update, _error_notification(_PDF_FAILED_MESSAGE)
