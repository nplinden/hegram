import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/paal_peh_yodvav")

(
    {
        "Personne": "",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
)

elements = [
    {
        "Personne": "1S",
        "Accompli": "יָלַדְתִּי",
        "Inaccompli": "אֵלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "יָלַדְתָּ",
        "Inaccompli": "תֵּלֵד",
        "Infinitif": "",
        "Impératif": "לֵד",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "יָלַדְתְּ",
        "Inaccompli": "תֵּלְדִי",
        "Infinitif": "",
        "Impératif": "לְדִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "יָלַד",
        "Inaccompli": "יֵלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "יוֹלֵד",
    },
    {
        "Personne": "3FS",
        "Accompli": "יָֽלְדָה",
        "Inaccompli": "תֵּלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "יוֹלֶדֶת",
    },
    {
        "Personne": "1P",
        "Accompli": "יָלַדְנוּ",
        "Inaccompli": "נֵלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "יְלַדְתֶּם",
        "Inaccompli": "תֵּלְדוּ",
        "Infinitif": "",
        "Impératif": "לְדוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "יְלַדְתֶּן",
        "Inaccompli": "תֵּלֵדְנָה, תֵּלַדְנָה",
        "Infinitif": "",
        "Impératif": "לֵדְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "יָֽלְדוּ",
        "Inaccompli": "יֵלְדוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "יוֹלְדִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "יָֽלְדוּ",
        "Inaccompli": "תֵּלֵדְנָה, תֵּלַדְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "יוֹלְדוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "יָלֹד",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "לָלֶדֶת",
        "Impératif": "",
        "P. Présent": "",
    },
]

rows = [
    dmc.TableTr(
        [
            dmc.TableTd(element["Personne"]),
            dmc.TableTd(element["Accompli"]),
            dmc.TableTd(element["Inaccompli"]),
            dmc.TableTd(element["Infinitif"]),
            dmc.TableTd(element["Impératif"]),
            dmc.TableTd(element["P. Présent"]),
        ]
    )
    for element in elements
]

head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Personne"),
            dmc.TableTh("Accompli"),
            dmc.TableTh("Inaccompli"),
            dmc.TableTh("Infinitif"),
            dmc.TableTh("Impératif"),
            dmc.TableTh("P. Présent"),
        ]
    )
)
body = dmc.TableTbody(rows)
caption = dmc.TableCaption("Conjugation of ילד in Paal")


layout = dmc.MantineProvider(
    dash.html.Div(
        children=[
            dmc.Table(
                [head, body, caption],
                className="conjugation-table",
            )
        ],
        className="conjugation-container",
    )
)
