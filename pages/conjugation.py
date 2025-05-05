import dash
import dash_mantine_components as dmc
from dash import html, no_update
import polars as pl
from bs4 import BeautifulSoup
from dash import callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from hegram.mechon_mamre import verse_to_url, en_to_fr_books
import requests

from hegram.data import dropdown_data, en_to_fr, answer_data
from hegram.definitions import definitions
from hegram.utils import convert_html_to_dash, htmlify
from hebrew import Hebrew

COMMON_BINYANIM = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]

dash.register_page(__name__, path="/conjugation")


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
    book = en_to_fr_books[df["book"]]
    chapter, verse = df["chapter"], df["verse"]
    url = verse_to_url(book, int(chapter))
    response = requests.get(url)
    if response.status_code != 200:
        return html.P([html.Em(["Can't retrieve french passage"])])
    else:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.find_all("table")[1].find("b", string=str(verse)).next_element.next_element.strip()
        return html.P([passage(verse_id), f" : {text}"])


@callback(
    Output("clause-div", "children"),
    Output("word-div", "children"),
    Output("solution-storage", "data"),
    Output("fullverse-div", "style"),
    Output("solution-alert", "style", allow_duplicate=True),
    Output("notification", "children"),
    Output("accordion", "value"),
    Output("answer-div", "style"),
    Output("frenchverse-div", "style"),
    Input("clause-btn", "n_clicks"),
    State("root-number", "value"),
    State("conjugation-book-dropdown", "value"),
    State("conjugation-binyan-dropdown", "value"),
    State("conjugation-tense-dropdown", "value"),
    State("conjugation-person-dropdown", "value"),
    State("conjugation-gender-dropdown", "value"),
    State("conjugation-number-dropdown", "value"),
    prevent_initial_call=True,
)
def generate_verb(clicked, max_roots, book, binyanim, tenses, persons, genders, numbers):
    if clicked is None:
        raise PreventUpdate
    df = pl.scan_parquet("data/conjugation.parquet")

    if max_roots:
        roots = (
            df.select([pl.col("Root").value_counts(sort=True)])
            .collect()
            .unnest(pl.col("Root"))
            .top_k(max_roots, by="count")
            .select(pl.col("Root"))
            .to_series()
        ).to_list()
    else:
        roots = []

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
            dmc.Notification(
                title="Erreur",
                action="show",
                message="Aucun verbe ne satisfait ces filtres !",
                icon=DashIconify(
                    icon="material-symbols:error-outline-rounded", color=dmc.DEFAULT_THEME["colors"]["dark"][6]
                ),
            ),
            "",
            no_update,
            no_update,
        )
    else:
        sample = filtered.sample(n=1).to_dicts()[0]
        verse, word = sample["VerseId"], sample["WordId"]
        return (
            build_verse(verse, word),
            build_word(word),
            sample,
            {"display": "block"},
            {"display": "none"},
            no_update,
            "",
            {"display": "flex"},
            {"display": "none"},
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


@callback(
    Output("frenchverse-div", "children"),
    Output("frenchverse-div", "style", allow_duplicate=True),
    Input("solution-btn", "n_clicks"),
    State("solution-storage", "data"),
    prevent_initial_call=True,
)
def show_frenchverse(n_clicks, data):
    if not n_clicks:
        raise PreventUpdate
    verse = data["VerseId"]
    return french_passage(verse), {"display": "block"}


@callback(
    Output("solution-alert", "children"),
    Output("solution-alert", "title"),
    Output("solution-alert", "style", allow_duplicate=True),
    Output("solution-alert", "color"),
    Input("solution-btn", "n_clicks"),
    State("solution-storage", "data"),
    State("root-answer", "value"),
    State("binyan-answer", "value"),
    State("tense-answer", "value"),
    State("person-answer", "value"),
    prevent_initial_call=True,
)
def show_solution(n_clicks, data, root_answer, binyan_answer, tense_answer, person_answer):
    if not n_clicks:
        raise PreventUpdate

    root = data["Root"]
    tense = en_to_fr["Tense"][data["Tense"]]
    binyan = data["Binyan"]
    number = {"Singular": "S", "Plural": "P"}.get(data["Number"], "")
    person = {"1": "1", "2": "2", "3": "3"}.get(data.get("Person", ""), "")
    gender = {"M": "M", "F": "F"}.get(data.get("Gender", ""), "")
    rest = f"{person}{gender}{number}"

    root_nodiacr = Hebrew(root).text_only()
    definition = definitions.get(str(root_nodiacr), [["No definition found"]])[0]
    html = ["<div>", "<p>Définition :</p>"]
    for d in definition:
        html.append(htmlify(d))
    html.append("</div>")
    html = "\n".join(html)

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

    results = True
    if binyan_answer is None or binyan_answer != binyan:
        results = False
    if root_answer is None or root_answer != root:
        results = False
    if tense_answer is None or tense_answer != data["Tense"]:
        results = False
    if person_answer is None:
        person_answer = ""
    if person_answer != rest:
        results = False

    color = "green" if results else "red"
    return [solution, convert_html_to_dash(html), chart], root, {"display": "block"}, color


def data_from_list(items):
    return [{"value": k, "label": k} for k in items]


def get_root_select_data():
    roots = pl.scan_parquet("data/conjugation.parquet").select(["Root"]).unique().sort(["Root"]).collect().to_series()
    data = [{"label": v, "value": v} for v in roots]
    return data


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

layout = dmc.MantineProvider(
    dash.html.Div(
        children=[
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
                                children=[
                                    html.H1("Exercice de conjugaison"),
                                    html.P(
                                        "Une application d'exercice à la conjugaison en hébreu biblique. Cliquez sur \"Trouver un verbe\" pour choisir aléatoirement une forme verbale dans le corpus biblique. Essayez d'analyser la conjugaison de ce verbe ! Le verset correspondant est également fourni pour plus de contexte."
                                    ),
                                    html.P(
                                        'Le menu "Paramètres" ci-dessous permet de restreindre le choix des formes verbales.'
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
                                children=[
                                    dmc.NumberInput(
                                        label="Niveau d'occurrence maximum autorisé (e.g. 50 n'autorise que les 50 racines les plus courantes)",
                                        min=0,
                                        id="root-number",
                                    ),
                                    book_select,
                                    binyan_select,
                                    tense_select,
                                    person_select,
                                    gender_select,
                                    number_select,
                                ]
                            ),
                        ],
                        value="settings",
                    ),
                ],
                mb=10,
                value="introduction",
                id="accordion",
            ),
            dmc.Flex(
                [
                    dmc.Button("Trouver un verbe", id="clause-btn", color=dmc.DEFAULT_THEME["colors"]["dark"][6]),
                ],
                direction={"base": "column", "sm": "row"},
                gap={"base": "sm", "sm": "lg"},
                justify={"sm": "center"},
                mb=10,
            ),
            # html.Div(
            #     [
            #         # html.P(
            #         #     [
            #         #         "Analysez cette forme verbale issue de ",
            #         #         html.Span(id="weblink-span"),
            #         #         ":",
            #         #     ]
            #         # ),
            #     ],
            #     style={"display": "none"},
            #     id="analyze-div",
            # ),
            html.Div(children=[], id="word-div", style={"textAlign": "center"}),
            html.Div(
                [
                    html.P("Verset complet:"),
                ],
                style={"display": "none"},
                id="fullverse-div",
            ),
            dmc.Flex(children=[], id="clause-div", className="fullverse", mb=10),
            dmc.Flex(
                [
                ],
                style={"display": "none"},
                id="frenchverse-div",
                className="frenchverse", mb=10
            ),
            dmc.Flex(
                children=[
                    dmc.Select(
                        placeholder="Racine", value=None, data=get_root_select_data(), searchable=True, id="root-answer"
                    ),
                    dmc.Select(placeholder="Binyan", value=None, data=dropdown_data["Binyan"], id="binyan-answer"),
                    dmc.Select(placeholder="Temps", value=None, data=dropdown_data["Tense"], id="tense-answer"),
                    dmc.Select(placeholder="Personne", value=None, data=answer_data, id="person-answer"),
                    dmc.Button(
                        "Ok",
                        id="solution-btn",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                    ),
                ],
                style={"display": "none"},
                direction={"base": "column", "sm": "row"},
                gap={"base": "sm", "sm": "lg"},
                justify={"sm": "center"},
                mb=10,
                id="answer-div",
            ),
            dcc.Store(id="solution-storage", storage_type="local"),
            html.Div(
                [
                    html.P(children=[], id="solution-p-root", style={"fontFamily": "serif"}),
                    html.P(
                        children=[],
                        id="solution-p-rest",
                    ),
                ]
            ),
            dmc.Alert(
                "",
                title="",
                color="red",
                id="solution-alert",
                style={"display": "none"},
                styles={"title": {"fontFamily": "serif", "fontSize": "3rem"}, "message": {"fontSize": "1rem"}},
            ),
        ],
        className="container",
    )
)
