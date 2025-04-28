import dash
import dash_mantine_components as dmc
import pandas as pd
from dash.dash_table import DataTable
from dash import dcc, Input, Output, callback
from pages.datatable_style import style

dash.register_page(__name__, path="/pual_strong")

accompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Accompli": [
            "יֻלַּדְתִּי",
            "יֻלַּדְתָּ",
            "יֻלַּדְתְּ",
            "יֻלַּדְ",
            "יֻלְּדָה",
            "יֻלַּדְנוּ",
            "יֻלַּדְתֶּם",
            "יֻלַּדְתֶּן",
            "יֻלְּדוּ",
            "יֻלְּדוּ",
        ],
    }
)
inaccompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Inaccompli": [
            "אֲיֻלַּד",
            "תְּיֻלַּד",
            "תְּיֻלְּדִי",
            "יְיֻלַּד",
            "תְּיֻלַּד",
            "נְיֻלַּד",
            "תְּיֻלְּדוּ",
            "תְּיֻלַּדְנָה",
            "יְיֻלְּדוּ",
            "תְּיֻלַּדְנָה",
        ],
    }
)

participe = pd.DataFrame(
    {
        "Personne": ["MS", "FS", "MP", "FP"],
        "P. Présent": [
            "מְיֻלַּד",
            "מְיֻלֶּדֶת",
            "מְיֻלָּדִים",
            "מְיֻלָּדוֹת",
        ],
    }
)

layout = dmc.MantineProvider(
    [
        dash.html.Div(
            children=[
                dash.html.H1(
                    "Un verbe fort au pual: דבר",
                ),
                dmc.Button("Télécharger en pdf", color="black", mb=10, id="button-pual-strong"),
                dcc.Download(id="download-pual-strong"),
                dash.html.Div(
                    [
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
    Output("download-pual-strong", "data"),
    Input("button-pual-strong", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("assets/pual_strong.svg")
