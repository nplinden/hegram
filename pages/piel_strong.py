import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/piel_strong")

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
        "Accompli": "דִּבַּרְתִּי",
        "Inaccompli": "אֲדַבֵּר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "דִּבַּרְתָּ",
        "Inaccompli": "תְּדַבֵּר",
        "Infinitif": "",
        "Impératif": "דַּבֵּר",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "דִּבַּרְתְּ",
        "Inaccompli": "תְּדַבְּרִי",
        "Infinitif": "",
        "Impératif": "דַּבְּרִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "דִּבֵּר",
        "Inaccompli": "יְדַבֵּר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְדַבֵּר",
    },
    {
        "Personne": "3FS",
        "Accompli": "דִּבְּרָה",
        "Inaccompli": "תְּדַבֵּר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְדַבֶּרֶת",
    },
    {
        "Personne": "1P",
        "Accompli": "דִּבַּרְנוּ",
        "Inaccompli": "נְדַבֵּר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "דִּבַּרְתֶּם",
        "Inaccompli": "תְּדַבֵּרוּ",
        "Infinitif": "",
        "Impératif": "דַּבְּרוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "דִּבַּרְתֶּן",
        "Inaccompli": "תְּדַבֵּרְנָה",
        "Infinitif": "",
        "Impératif": "דַּבֵּרְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "דִּבְּרוּ",
        "Inaccompli": "יְדַבֵּרוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְדַבְּרִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "דִּבְּרוּ",
        "Inaccompli": "תְּדַבֵּרְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מְדַבְּרוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "דַּבֵּר",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "לְדַבֵּר",
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
caption = dmc.TableCaption("Conjugation of דבר in Piel")


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
