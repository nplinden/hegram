import dash
import dash_mantine_components as dmc
import pandas as pd
from dash.dash_table import DataTable
from dash import dcc, Input, Output, callback
from pages.datatable_style import style

dash.register_page(__name__, path="/niphal_peh_yodvav")

accompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Accompli": [
            "נוֹלַדְתִּי",
            "נוֹלַדְתָּ",
            "נוֹלַדְתְּ",
            "נוֹלַד",
            "נוֹלְדָה",
            "נוֹלַדְנוּ",
            "נוֹלַדְתֶּם",
            "נוֹלַדְתֶּן",
            "נוֹלְדוּ",
            "נוֹלְדוּ",
        ],
    }
)
inaccompli = pd.DataFrame(
    {
        "Personne": ["1S", "2MS", "2FS", "3MS", "3FS", "1P", "2MP", "2FP", "3MP", "3FS"],
        "Inaccompli": [
            "אִוָּלַד",
            "תִּוָּלֵד",
            "תִּוָּֽלְדִי",
            "יִוָּלֵד",
            "תִּוָּלֵד",
            "נִוָּלֵד",
            "תִּוָּֽלְדוּ",
            "תִּוָּלַדְנָה",
            "יִוָּֽלְדוּ",
            "תִּוָּלַדְנָה",
        ],
    }
)

imperatif = pd.DataFrame(
    {
        "Personne": ["2MS", "2FS", "2MP", "2FP"],
        "Impératif": [
            "הִוָּלֵד",
            "הִוָּֽלְדִי",
            "הֹוָּֽלְדוּ",
            "הִוָּלֵדְנָה, הִוָּלַדְנָה",
        ],
    }
)

participe = pd.DataFrame(
    {
        "Personne": ["MS", "FS", "MP", "FP"],
        "P. Présent": [
            "נוֹלָד",
            "נוֹלֶדֶת, נוּלָדָה",
            "נוֹלָדִים",
            "נוֹלָדוֹת",
        ],
    }
)

absolu = pd.DataFrame(
    {
        "Infinitif absolu": ["נוֹלוֹד"],
    }
)

construit = pd.DataFrame({"Infinitif construit": ["הִוָּלֵד"]})

layout = dmc.MantineProvider(
    [
        dash.html.Div(
            children=[
                dash.html.H1(
                    "Un verbe פ’’יו au niphal: ילד",
                ),
                dmc.Button("Télécharger en pdf", color="black", mb=10, id="button-niphal-peh_yodvav"),
                dcc.Download(id="download-niphal-peh_yodvav"),
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
    Output("download-niphal-peh_yodvav", "data"),
    Input("button-niphal-peh_yodvav", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file("assets/niphal_peh_yodvav.svg")
