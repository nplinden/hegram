import base64 as _b64
import os as _os
import weasyprint as _weasyprint
import dash
import dash_mantine_components as dmc
import json as _json
from html import escape as _escape
from dash import html, no_update
import polars as pl
from bs4 import BeautifulSoup, NavigableString
from dash import callback, Input, Output, State, dcc, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from loguru import logger
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


_HEBREW_CONSONANTS = set(chr(c) for c in range(0x05D0, 0x05EB))


_NO_VERB_MESSAGE = "Aucun verbe ne satisfait ces filtres !"
_NO_QUESTION_COUNT_MESSAGE = "Indiquez un nombre de questions."
_PDF_FAILED_MESSAGE = "La génération du PDF a échoué. Veuillez réessayer."


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


def _hl(span):
    span["class"].append("hl")
    if span.string and span.string.endswith(" "):
        span.string.replace_with(span.string[:-1])
        span.insert_after(NavigableString(" "))


def _verse_words(verse_rows: list[dict]) -> dict[int, str]:
    """Fetch the html of every word in the given verses, keyed by word id."""
    in_verses = pl.any_horizontal([pl.col("id").is_between(r["WordId_min"], r["WordId_max"]) for r in verse_rows])
    df = pl.scan_parquet("data/words.parquet").filter(in_verses).select(["id", "html"]).collect()
    return dict(df.iter_rows())


def build_verse(verse_id, word_id):
    verse_row = pl.scan_parquet("data/verses.parquet").filter(pl.col("id") == verse_id).collect().to_dicts()[0]
    return convert_html_to_dash(_build_verse_html(verse_row, _verse_words([verse_row]), word_id))


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


def _verse_ref(verse_row: dict) -> str:
    book = en_to_fr_books[verse_row["book"]]
    return f"{book} {verse_row['chapter']}:{verse_row['verse']}"


def _build_verse_html(verse_row: dict, words_html: dict[int, str], word_id: int) -> str:
    # Rebuild the verse word by word rather than searching the verse html for the
    # verb's text: the same form can occur several times in a verse, and the verse
    # html sometimes merges several words into a single span.
    soup = BeautifulSoup('<div class="fullverse"></div>', features="html.parser")
    prev = target = None
    for wid in range(verse_row["WordId_min"], verse_row["WordId_max"] + 1):
        span = BeautifulSoup(words_html[wid], features="html.parser").find("span")
        if span is None:  # word with no surface text, e.g. an elided article
            continue
        soup.div.append(span)
        if wid < word_id:
            prev = span
        elif wid == word_id:
            target = span
    _hl(target)
    if prev is not None:
        consonants = [c for c in prev.get_text() if c in _HEBREW_CONSONANTS]
        if consonants == ["\u05d5"]:  # single vav — prefix of wayyiqtol/waw-consecutive
            _hl(prev)
    return str(soup)


def _hebrew_numeral(n: int) -> str:
    if n <= 0:
        return str(n)

    ones = {1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט"}
    tens = {10: "י", 20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ"}
    hundreds = {100: "ק", 200: "ר", 300: "ש", 400: "ת"}

    letters = []

    while n >= 400:
        letters.append(hundreds[400])
        n -= 400

    for value in (300, 200, 100):
        if n >= value:
            letters.append(hundreds[value])
            n -= value

    if n == 15:
        letters.append("טו")
        n = 0
    elif n == 16:
        letters.append("טז")
        n = 0

    if n:
        for value in (90, 80, 70, 60, 50, 40, 30, 20, 10):
            if n >= value:
                letters.append(tens[value])
                n -= value
                break
        if n:
            letters.append(ones[n])

    raw = "".join(letters)
    if len(raw) == 1:
        return raw
    return raw


def _sample_person_label(row: dict) -> str:
    number = {"Singular": "S", "Plural": "P"}.get(row.get("Number", ""), "")
    person = {"1": "1", "2": "2", "3": "3"}.get(str(row.get("Person", "")), "")
    gender = {"M": "M", "F": "F"}.get(row.get("Gender", ""), "")
    return f"{person}{gender}{number}" or "—"


def _build_pdf_html(samples: list[dict], *, with_answers: bool = False) -> str:
    verse_ids = list({s["VerseId"] for s in samples})
    verses = {
        r["id"]: r
        for r in pl.scan_parquet("data/verses.parquet").filter(pl.col("id").is_in(verse_ids)).collect().to_dicts()
    }
    words = _verse_words(list(verses.values()))
    answer_labels = ["Racine", "Binyan", "Temps", "Personne"]
    questions_html = ""
    for i, s in enumerate(samples, 1):
        verse_html = _build_verse_html(verses[s["VerseId"]], words, s["WordId"])
        ref = _verse_ref(verses[s["VerseId"]])
        if with_answers:
            answer_values = {
                "Racine": s["Root"],
                "Binyan": s["Binyan"],
                "Temps": en_to_fr["Tense"].get(s["Tense"], s["Tense"]),
                "Personne": _sample_person_label(s),
            }
            answer_fields = "".join(
                f'<div class="answer-field">'
                f'<span class="answer-label">{label} :</span>'
                f'<span class="answer-value">{_escape(str(answer_values[label]))}</span>'
                f"</div>"
                for label in answer_labels
            )
        else:
            answer_fields = "".join(
                f'<label class="answer-field" for="q{i}-{label.lower()}">'
                f'<span class="answer-label">{label} :</span>'
                f'<input class="answer-input" id="q{i}-{label.lower()}" name="q{i}-{label.lower()}" type="text" />'
                f"</label>"
                for label in answer_labels
            )
        qnum_he = _hebrew_numeral(i)
        questions_html += f"""
<div class="question">
    <div class="question-number-he">{qnum_he}</div>
  <div class="cards-row">
    <div class="answer-section">{answer_fields}</div>
    <div class="verse-card">
      {verse_html}
      <div class="verse-ref">{ref}</div>
    </div>
  </div>
</div>"""
    css = """
@font-face {
  font-family: "Ezra SIL";
  src: url("SILEOT.woff");
  unicode-range: U+0590-U+05FF, U+FB1D-U+FB4F;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Ezra SIL", sans-serif; background: white; color: #000; padding: 12mm 15mm; }
.question, .question * { color: #000; }
.question {
  display: flex;
  flex-direction: column;
  gap: 8px;
    position: relative;
    padding-right: 12mm;
    padding-bottom: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid #ddd;
  break-inside: avoid;
}
.question:last-child {
    border-bottom: none;
    margin-bottom: 0;
}
.question-number-he {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    font-family: "Ezra SIL", sans-serif;
    font-size: 1rem;
    color: #000;
    line-height: 1;
}
.cards-row {
  display: flex;
  gap: 12px;
    align-items: flex-start;
  width: 100%;
    min-width: 0;
}
.verb-card {
  flex: 0 0 25%;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.verse-card {
  flex: 0 0 calc(75% - 12px);
    align-self: stretch;
  min-width: 0;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 12px;
}
.singleword {
  font-family: "Ezra SIL", sans-serif;
  font-size: 1.6rem;
  direction: rtl;
}
.fullverse {
  font-family: "Ezra SIL", sans-serif;
  font-size: 1rem;
  direction: rtl;
  line-height: 1.5;
}
.hl {
  background-color: rgba(147, 197, 253, 0.6);
  border-radius: 2px;
}
.verse-ref {
  font-style: italic;
  font-size: 0.7rem;
    color: #000;
  margin-top: 4px;
  direction: ltr;
}
.answer-section {
  flex: 0 0 25%;
    min-width: 0;
    max-width: 25%;
  display: flex;
  flex-direction: column;
    justify-content: flex-start;
  gap: 6px;
}
.answer-field {
        flex: 0 0 auto;
    display: grid;
    grid-template-columns: max-content 1fr;
    align-items: end;
    column-gap: 4px;
    min-width: 0;
}
.answer-label {
  font-size: 0.6rem;
  font-weight: 600;
    color: #000;
  white-space: nowrap;
  line-height: 1;
}
.answer-value {
        width: 100%;
        min-width: 0;
        border-bottom: 2px solid #888;
        padding: 1px 2px;
        font-size: 0.9rem;
        font-family: sans-serif;
        line-height: 1.2;
}
.answer-input {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    border: none;
    border-bottom: 2px solid #888;
    border-radius: 0;
    background: transparent;
    padding: 1px 2px;
    font-size: 0.9rem;
    font-family: sans-serif;
    line-height: 1.2;
    appearance: auto;
    -webkit-appearance: auto;
}
input,
select,
textarea,
button {
    appearance: auto;
    -webkit-appearance: auto;
}
@media print {
  body { margin: 0; padding: 10mm 12mm; }
}
"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Exercice de conjugaison</title>
<style>{css}</style>
</head>
<body>
{questions_html}
</body>
</html>"""


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


def _compute_root_freq_data():
    df = (
        pl.scan_parquet("data/conjugation.parquet")
        .group_by("Root")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
        .collect()
    )
    return df["Root"].to_list(), df["count"].to_list()


_ROOTS_BY_FREQ, _ROOT_COUNTS = _compute_root_freq_data()
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
                        dmc.Divider(my=12),
                        dmc.Group(
                            [
                                dmc.NumberInput(
                                    id="conj-pdf-n-questions",
                                    label="Nombre de questions",
                                    min=1,
                                    max=50,
                                    step=1,
                                    value=10,
                                    style={"width": 160},
                                ),
                                dmc.Stack(
                                    [
                                        dmc.Button(
                                            "Télécharger questionnaire",
                                            id="conj-pdf-btn",
                                            leftSection=DashIconify(icon="material-symbols:download", width=18),
                                            variant="outline",
                                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                                        ),
                                        dmc.Button(
                                            "Télécharger corrigé",
                                            id="conj-correction-btn",
                                            leftSection=DashIconify(icon="material-symbols:download", width=18),
                                            variant="light",
                                            color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                                        ),
                                    ],
                                    gap="xs",
                                    style={"alignSelf": "flex-end"},
                                ),
                            ],
                            align="flex-end",
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
            return no_update, no_update, _error_notification(_NO_VERB_MESSAGE)
        k = min(int(n_questions), len(filtered))
        samples = filtered.sample(n=k).to_dicts()
        html_content = _build_pdf_html(samples, with_answers=False)
        assets_dir = _os.path.abspath("assets")
        pdf_bytes = _weasyprint.HTML(string=html_content, base_url=assets_dir).write_pdf(pdf_forms=True)
        return dcc.send_bytes(pdf_bytes, filename="questionnaire_conjugaison.pdf"), samples, no_update
    except Exception:
        logger.exception("PDF generation failed")
        return no_update, no_update, _error_notification(_PDF_FAILED_MESSAGE)


@callback(
    Output("conj-correction-download", "data"),
    Output("notification", "children", allow_duplicate=True),
    Input("conj-correction-btn", "n_clicks"),
    State("conj-pdf-samples", "data"),
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
def generate_correction_pdf(
    n_clicks, saved_samples, n_questions, roots, book, binyanim, tenses, persons, genders, numbers
):
    # See generate_pdf: only act on an actual click.
    if not n_clicks:
        raise PreventUpdate
    if not saved_samples and not n_questions:
        return no_update, _error_notification(_NO_QUESTION_COUNT_MESSAGE)
    try:
        if saved_samples:
            samples = saved_samples
        else:
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
                return no_update, _error_notification(_NO_VERB_MESSAGE)
            k = min(int(n_questions), len(filtered))
            samples = filtered.sample(n=k).to_dicts()
        html_content = _build_pdf_html(samples, with_answers=True)
        assets_dir = _os.path.abspath("assets")
        pdf_bytes = _weasyprint.HTML(string=html_content, base_url=assets_dir).write_pdf()
        return dcc.send_bytes(pdf_bytes, filename="corrige_conjugaison.pdf"), no_update
    except Exception:
        logger.exception("Correction PDF generation failed")
        return no_update, _error_notification(_PDF_FAILED_MESSAGE)
