import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/poual_strong")

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
        "Accompli": "יֻלַּדְתִּי",
        "Inaccompli": "אֲיֻלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "יֻלַּדְתָּ",
        "Inaccompli": "תְּיֻלַּד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "יֻלַּדְתְּ",
        "Inaccompli": "תְּיֻלְּדִי",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "יֻלַּד",
        "Inaccompli": "יְיֻלַּד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְיֻלַּד",
    },
    {
        "Personne": "3FS",
        "Accompli": "יֻלְּדָה",
        "Inaccompli": "תְּיֻלַּד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְיֻלֶּדֶת",
    },
    {
        "Personne": "1P",
        "Accompli": "יֻלַּדְנוּ",
        "Inaccompli": "נְיֻלַּד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "יֻלַּדְתֶּם",
        "Inaccompli": "תְּיֻלְּדוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "יֻלַּדְתֶּן",
        "Inaccompli": "תְּיֻלַּדְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "יֻלְּדוּ",
        "Inaccompli": "תּיֻלְּדוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְיֻלָּדִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "יֻלְּדוּ",
        "Inaccompli": "תְּיֻלַּדְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְיֻלָּדוֹת",
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
caption = dmc.TableCaption("Conjugation of ילד in Poual")


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
