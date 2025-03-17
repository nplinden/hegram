import dash
import dash_mantine_components as dmc
from dash import html
from tf.app import use
import pandas as pd
from random import randint
from bs4 import BeautifulSoup
from hegram.conjugation import conjugation, A
from xml.etree import ElementTree
from dash import callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify


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
    name, href = A.webLink(element_id, _asString=True).split(" => ")
    return html.A(
        children=[name.replace("_", " ")],
        href=href,
        target="_blank",
        className="manual-link",
    )


@callback(
    Output("clause-div", "children"),
    Output("weblink-span", "children"),
    Output("word-div", "children"),
    Output("solution-storage", "data"),
    Input("clause-btn", "n_clicks"),
    State("root-number", "value"),
    State("conjugation-book-dropdown", "value"),
    State("conjugation-binyan-dropdown", "value"),
    State("conjugation-tense-dropdown", "value"),
    State("conjugation-person-dropdown", "value"),
    State("conjugation-gender-dropdown", "value"),
    State("conjugation-number-dropdown", "value"),
)
def generate_verb(clicked, max_roots, book, binyanim, tenses, persons, genders, numbers):
    df = conjugation
    if book:
        df = df[df["Book"].isin(book)]
    if binyanim:
        df = df[df["Binyan"].isin(binyanim)]
    if tenses:
        df = df[df["Tense"].isin(tenses)]
    if persons:
        df = df[df["Person"].isin(persons)]
    if genders:
        df = df[df["Gender"].isin(genders)]
    if numbers:
        df = df[df["Number"].isin(numbers)]
    if max_roots:
        roots = list(df["Root"].value_counts().sort_values(ascending=False).index[:max_roots])
        df = df[df["Root"].isin(roots)]

    print(df.head())
    row = df.iloc[randint(0, len(df) - 1)]
    print(row.to_dict())
    verse, word = int(row.VerseId), int(row.WordId)
    return get_verse(verse, word), passage(word), get_verse(word), row.to_dict()


@callback(Output("solution-body", "children"), Input("solution-btn", "n_clicks"), State("solution-storage", "data"))
def show_solution(n_clicks, data):
    if not n_clicks:
        raise PreventUpdate
    return [
        dmc.TableTr(
            [
                dmc.TableTd(data["Root"]),
                dmc.TableTd(data["Binyan"]),
                dmc.TableTd(data["Tense"]),
                dmc.TableTd(data["Person"]),
                dmc.TableTd(data["Gender"]),
                dmc.TableTd(data["Number"]),
            ]
        )
    ]


def data_from_list(items):
    return [{"value": k, "label": k} for k in items]


book_select = dmc.MultiSelect(
    label="Livres autorisés",
    data=data_from_list(sorted(pd.unique(conjugation["Book"]))),
    value=[],
    id="conjugation-book-dropdown",
    mb=10,
)

binyan_select = dmc.MultiSelect(
    label="Binyanim autorisés",
    data=data_from_list(sorted(pd.unique(conjugation["Binyan"]))),
    value=[],
    id="conjugation-binyan-dropdown",
    mb=10,
)

tense_select = dmc.MultiSelect(
    label="Temps autorisés",
    data=data_from_list(sorted(pd.unique(conjugation["Tense"]))),
    value=[],
    id="conjugation-tense-dropdown",
    mb=10,
)

person_select = dmc.MultiSelect(
    label="Personnes autorisées",
    data=data_from_list(sorted(pd.unique(conjugation["Person"]))),
    value=[],
    id="conjugation-person-dropdown",
    mb=10,
)

gender_select = dmc.MultiSelect(
    label="Genres autorisés",
    data=data_from_list(sorted(pd.unique(conjugation["Gender"]))),
    value=[],
    id="conjugation-gender-dropdown",
    mb=10,
)

number_select = dmc.MultiSelect(
    label="Nombres autorisées",
    data=data_from_list(sorted(pd.unique(conjugation["Number"]))),
    value=[],
    id="conjugation-number-dropdown",
    mb=10,
)

solution_head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Racine"),
            dmc.TableTh("Binyan"),
            dmc.TableTh("Tense"),
            dmc.TableTh("Person"),
            dmc.TableTh("Gender"),
            dmc.TableTh("Number"),
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
            html.H1("Exercice de conjugaison"),
            html.P(
                "Une application d'exercice à la conjugaison en hébreu biblique. Cliquez sur \"Trouver un verbe\" pour choisir aléatoirement une forme verbale dans le corpus biblique. Essayez d'analyser la conjugaison de ce verbe! Le verset correspondant est également fourni pour plus de contexte."
            ),
            html.P('Le menu "Paramètres" ci-dessous permet de restreindre le choix des formes verbales.'),
            dmc.Accordion(
                disableChevronRotation=True,
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
            html.Div(
                [dmc.Button("Trouver un verbe", id="clause-btn")],
            ),
            html.P(
                [
                    "Analysez cette forme verbale issue de ",
                    html.Span(id="weblink-span"),
                    ":",
                ]
            ),
            html.Div(children=[], id="word-div", style={"textAlign": "center"}),
            html.P("Verset complet:"),
            html.Div(children=[], id="clause-div", style={}),
            html.Div(
                [dmc.Button("Afficher la solution", id="solution-btn")],
            ),
            dcc.Store(id="solution-storage", storage_type="local"),
            dmc.Table([solution_head, solution_body], className="conjugation-table"),
        ],
        className="container",
    )
)
