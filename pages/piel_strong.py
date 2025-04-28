import dash
import dash_mantine_components as dmc
import pandas as pd
from dash.dash_table import DataTable
from dash import dcc, Input, Output, callback
from pages.datatable_style import style

dash.register_page(__name__, path="/piel_strong")

accompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Accompli": [
            "דִּבַּרְתִּי",
            "דִּבַּרְתָּ",
            "דִּבַּרְתְּ",
            "דִּבֵּר",
            "דִּבְּרָה",
            "דִּבַּרְנוּ",
            "דִּבַּרְתֶּם",
            "דִּבַּרְתֶּן",
            "דִּבְּרוּ",
            "דִּבְּרוּ",
        ],
    }
)
inaccompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Inaccompli": [
            "אֲדַבֵּר",
            "תְּדַבֵּר",
            "תְּדַבְּרִי",
            "יְדַבֵּר",
            "תְּדַבֵּר",
            "נְדַבֵּר",
            "תְּדַבֵּרוּ",
            "תְּדַבֵּרְנָה",
            "יְדַבֵּרוּ",
            "תְּדַבֵּרְנָה",
        ],
    }
)

imperatif = pd.DataFrame(
    {
        "Personne": ["2MS", "2FS", "2MP", "2FP"],
        "Impératif": [
            "דַּבֵּר",
            "דַּבְּרִי",
            "דַּבְּרוּ",
            "דַּבֵּרְנָה",
        ],
    }
)

participe = pd.DataFrame(
    {
        "Personne": ["MS", "FS", "MP", "FP"],
        "P. Présent": [
            "מְדַבֵּר",
            "מְדַבֶּרֶת",
            "מְדַבְּרִים",
            "מְדַבְּרוֹת",
        ],
    }
)

absolu = pd.DataFrame(
    {
        "Infinitif absolu": ["דַּבֵּר"],
    }
)

construit = pd.DataFrame({"Infinitif construit": ["לְדַבֵּר"]})

layout = dmc.MantineProvider(
    [
        dash.html.Div(
            children=[
                dash.html.H1(
                    "Un verbe fort au piel: דבר",
                ),
                dmc.Button("Télécharger en pdf", color="black", mb=10, id="button-piel-strong"),
                dcc.Download(id="download-piel-strong"),
                dash.html.Div(
                    [
                        DataTable(
                            data=absolu.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in absolu.columns],
                            **style,
                        ),
                        DataTable(
                            data=construit.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in construit.columns],
                            **style,
                        ),
                        DataTable(
                            data=accompli.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in accompli.columns],
                            **style,
                        ),
                        DataTable(
                            data=inaccompli.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in inaccompli.columns],
                            **style,
                        ),
                        DataTable(
                            data=imperatif.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in imperatif.columns],
                            **style,
                        ),
                        DataTable(
                            data=participe.to_dict("records"),
                            columns=[{"name": i, "id": i} for i in participe.columns],
                            **style,
                        ),
                    ],
                ),
            ],
            style={"font-family": "Ezra SIL", "maxWidth": "800px", "margin": "auto", "padding": "5px"},
        )
    ]
)


@callback(
    Output("download-piel-strong", "data"),
    Input("button-piel-strong", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("assets/piel_strong.svg")
