import dash
import dash_mantine_components as dmc
import pandas as pd
from dash.dash_table import DataTable
from dash import dcc, Input, Output, callback

dash.register_page(__name__, path="/paal_strong")

accompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Accompli": ["שָׁמַרְתִּי", "שָׁמַרְתָּ", "שָׁמַרְתְּ", "שָׁמַר", "שָׁמְרָה", "שָׁמַרְנוּ", "שָׁמַרְתֶּם",
                     "שָׁמַרְתֶּן", "שָׁמְרוּ", "שָׁמְרוּ"],
    }
)
inaccompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Inaccompli": [
            "אֶשְׁמֹר",
            "תִּשְׁמֹר",
            "תִּשְׁמְרִי",
            "יִשְׁמֹר",
            "תִּשְׁמֹר",
            "נִשְׁמֹר",
            "תִּשְׁמְרוּ",
            "תִּשְׁמֶרְנָה",
            "יִשְׁמְרוּ",
            "תִּשְׁמֶרְנָה",
        ],
    }
)

imperatif = pd.DataFrame(
    {
        "Personne": ["2MS", "2FS", "2MP", "2FP"],
        "Impératif": [
            "שְׁמֹר",
            "שִׁמְרִי",
            "שִׁמְרוּ",
            "שִׁמֶרְנָה",
        ],
    }
)

participe = pd.DataFrame(
    {
        "Personne": ["MS", "FS", "MP", "FP"],
        "P. Présent": [
            "שׁוֹמֵר",
            "שׁוֹמֶרֶת",
            "שׁוֹמְרִים",
            "שׁוֹמְרוֹת",
        ],
    }
)

absolu = pd.DataFrame(
    {
        "Infinitif absolu": ["שָׁמוֹר"],
    }
)

construit = pd.DataFrame({"Infinitif construit": ["(לִ)" + "שְׁמֹר"]})

style = {
    "style_table": {"maxWidth": "800px", "margin": "auto", "padding": "5px"},
    "style_cell": {
        "textAlign": "center",
        "padding-left": "8px",
        "padding-right": "8px",
        "border": "1px solid black",
        "font-family": "Ezra SIL",
        "font-size": "2rem",
        "direction": "rtl",
        "userSelect": "text",
    },
    "style_header": {"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
    "cell_selectable": False,
    "style_cell_conditional": [
        {"if": {"column_id": "Personne"}, "width": "20%"},
    ],
}


@callback(
    Output("download-paal-strong", "data"),
    Input("button-paal-strong", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("assets/paal_strong.svg")


layout = dmc.MantineProvider(
    [
        dash.html.Div(
            children=[
                dash.html.H1(
                    "Les verbes forts au paal: שׁמר",
                ),
                dmc.Button("Télécharger en pdf", color="black", mb=10, id="button-paal-strong"),
                dcc.Download(id="download-paal-strong"),
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
