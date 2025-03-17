import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/hiphil_strong")

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
        "Accompli": "הִמְלַכְתִּי",
        "Inaccompli": "אַמְלִיךְ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "הִמְלַכְתָּ",
        "Inaccompli": "תַּמְלִיךְ",
        "Infinitif": "",
        "Impératif": "הַמְלֵךְ",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "הִמְלַכְתְּ",
        "Inaccompli": "תַּמְלִיכִי",
        "Infinitif": "",
        "Impératif": "הַמְלִיכִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "הִמְלִיךְ",
        "Inaccompli": "יַמְלִיךְ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מַמְלִיךְ",
    },
    {
        "Personne": "3FS",
        "Accompli": "הִמְלִיכָה",
        "Inaccompli": "תַּמְלִיךְ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מַמְלִיכָה",
    },
    {
        "Personne": "1P",
        "Accompli": "הִמְלַכְנוּ",
        "Inaccompli": "נַמְלִיךְ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "הִמְלַכְתֶּם",
        "Inaccompli": "תַּמְלִיכוּ",
        "Infinitif": "",
        "Impératif": "הַמְלִיכוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "הִמְלַכְתֶּן",
        "Inaccompli": "תַּמְלֵכְנָה",
        "Infinitif": "",
        "Impératif": "הַמְלַכְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "הִמְלִיכוּ",
        "Inaccompli": "יַמְלִיכוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מַמְלִיכִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "הִמְלִיכוּ",
        "Inaccompli": "תַּמְלֵכְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "מַמְלִיכוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "הַמְלֵךְ",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "לְהַמְלִיךְ",
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
caption = dmc.TableCaption("Conjugation of מלכ in Hiphil")


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
