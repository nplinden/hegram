import dash
import dash_mantine_components as dmc
from dash import html, dash_table, no_update
import polars as pl
from bs4 import BeautifulSoup
from hegram.conjugation import A
from xml.etree import ElementTree
from dash import callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from hegram.mechon_mamre import verse_to_url, en_to_fr_books
from hegram.data import dropdown_data, en_to_fr


dash.register_page(__name__, path="/conjugation")


def convert_html_to_dash(html_code):
    """Convert standard html to Dash components"""

    def parse_css(css):
        """Convert a style in ccs format to dictionary accepted by Dash"""
        return {k: v for style in css.strip(";").split(";") for k, v in [style.split(":")]}

    def _convert(elem):
        comp = getattr(html, elem.tag.capitalize())
        children = [_convert(child) for child in elem]
        if not children:
            children = elem.text
        attribs = elem.attrib.copy()
        if "class" in attribs:
            attribs["className"] = attribs.pop("class")
        attribs = {k: (parse_css(v) if k == "style" else v) for k, v in attribs.items()}

        return comp(children=children, **attribs)

    et = ElementTree.fromstring(html_code)

    return _convert(et)


def get_verse(verse_id, word_id=None):
    if word_id is not None:
        html = BeautifulSoup(
            A.plain(verse_id, highlights={word_id}, _asString=True, withPassage=False),
            features="html.parser",
        )
    else:
        html = BeautifulSoup(
            A.plain(verse_id, _asString=True, withPassage=False),
            features="html.parser",
        )
    return convert_html_to_dash(str(html))


def passage(element_id: int):
    section = A.sectionStrFromNode(element_id)
    book = en_to_fr_books[section.split()[0]]
    chapter, verse = section.split()[1].split(":")
    name = f"{book} {chapter}:{verse}"
    url = verse_to_url(book, int(chapter))

    print(name, url)
    return html.A(
        children=[name],
        href=url,
        target="_blank",
        className="manual-link",
    )


@callback(
    Output("clause-div", "children"),
    Output("weblink-span", "children"),
    Output("word-div", "children"),
    Output("solution-storage", "data"),
    Output("analyze-div", "style"),
    Output("fullverse-div", "style"),
    Output("solution-datatable-div", "style", allow_duplicate=True),
    Output("notification", "children"),
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
            no_update,
            no_update,
            dmc.Notification(
                title="Erreur",
                action="show",
                message="Aucun verbe ne satisfait ces filtres !",
                icon=DashIconify(icon="material-symbols:error-outline-rounded"),
            ),
        )
    else:
        sample = filtered.sample(n=1).to_dicts()[0]
        print(sample)
        verse, word = sample["VerseId"], sample["WordId"]
        return (
            get_verse(verse, word),
            passage(word),
            get_verse(word),
            sample,
            {"display": "block"},
            {"display": "block"},
            {"display": "none"},
            no_update,
        )


@callback(
    Output("solution-datatable", "data"),
    Output("solution-datatable", "columns"),
    Output("solution-datatable-div", "style", allow_duplicate=True),
    Input("solution-btn", "n_clicks"),
    State("solution-storage", "data"),
    prevent_initial_call=True,
)
def show_solution(n_clicks, data):
    print(data)
    if not n_clicks:
        raise PreventUpdate
    df = pl.DataFrame(
        data=[
            [
                data["Root"],
                data["Binyan"],
                en_to_fr["Tense"][data["Tense"]],
                en_to_fr["Person"].get(data["Person"], "N/A"),
                en_to_fr["Gender"].get(data["Gender"], "N/A"),
                en_to_fr["Number"].get(data["Number"], "N/A"),
            ]
        ],
        schema=["Racine", "Binyan", "Temps", "Personne", "Genre", "Nombre"],
        orient="row",
    )
    return [
        df.to_dicts(),
        [{"name": c, "id": c} for c in df.columns],
        {"display": "block"},
    ]


def data_from_list(items):
    return [{"value": k, "label": k} for k in items]


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
                                    color=dmc.DEFAULT_THEME["colors"]["blue"][6],
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
                ],
                mb=10,
                value="introduction",
            ),
            dmc.Accordion(
                disableChevronRotation=False,
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(
                                "Paramètres",
                                icon=DashIconify(
                                    icon="material-symbols:settings",
                                    color=dmc.DEFAULT_THEME["colors"]["blue"][6],
                                    width=20,
                                ),
                            ),
                            dmc.AccordionPanel(
                                children=[
                                    dmc.NumberInput(
                                        label="Niveau d'occurence maximum autorisé (e.g. 50 n'autorise que les 50 racines les plus courantes)",
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
            ),
            dmc.Flex(
                [
                    dmc.Button("Trouver un verbe", id="clause-btn"),
                    dmc.Button("Afficher la solution", id="solution-btn"),
                ],
                direction={"base": "column", "sm": "row"},
                gap={"base": "sm", "sm": "lg"},
                justify={"sm": "center"},
                mb=10,
            ),
            html.Div(
                [
                    html.P(
                        [
                            "Analysez cette forme verbale issue de ",
                            html.Span(id="weblink-span"),
                            ":",
                        ]
                    ),
                ],
                style={"display": "none"},
                id="analyze-div",
            ),
            html.Div(children=[], id="word-div", style={"textAlign": "center"}),
            html.Div(
                [
                    html.P("Verset complet:"),
                ],
                style={"display": "none"},
                id="fullverse-div",
            ),
            html.Div(children=[], id="clause-div", style={}),
            dcc.Store(id="solution-storage", storage_type="local"),
            html.Div(
                dash_table.DataTable(
                    id="solution-datatable", style_cell={"fontSize": "2.5rem", "font-family": "serif"}
                ),
                id="solution-datatable-div",
                style={"display": "none"},
            ),
        ],
        className="container",
    )
)
