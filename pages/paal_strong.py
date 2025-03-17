import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/paal_strong")

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
        "Accompli": "שָׁמַ֫רְתִּי",
        "Inaccompli": "אֶשְׁמֹר",
        "Infinitif": None,
        "Impératif": None,
        "P. Présent": None,
    },
    {
        "Personne": "2MS",
        "Accompli": "שָׁמַ֫רְתָּ",
        "Inaccompli": "תִּשְׁמֹר",
        "Infinitif": "",
        "Impératif": "שְׁמֹר",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "שָׁמַרְתְּ",
        "Inaccompli": "תִּשְׁמְרִי",
        "Infinitif": "",
        "Impératif": "שִׁמְרִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "שָׁמַר",
        "Inaccompli": "יִשְׁמֹר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "שֹׁמֵר",
    },
    {
        "Personne": "3FS",
        "Accompli": "שָֽׁמְרָה",
        "Inaccompli": "תִּשְׁמֹר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "שֹׁמֶרֶת",
    },
    {
        "Personne": "1P",
        "Accompli": "שָׁמַ֫רְנוּ",
        "Inaccompli": "נִשְׁמֹר",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "שְׁמַרְתֶּם",
        "Inaccompli": "תִּשְׁמְרוּ",
        "Infinitif": "",
        "Impératif": "שִׁמְרוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "שְׁמַרְתֶּן",
        "Inaccompli": "תִּשְׁמֹרְנָה",
        "Infinitif": "",
        "Impératif": "שְׁמֹרְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "שָֽׁמְרוּ",
        "Inaccompli": "יִשְׁמְרוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "שֹׁמְרִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "שָֽׁמְרוּ",
        "Inaccompli": "תִּשְׁמֹרְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "שֹׁמְרוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "שָׁמוֹר",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "(לִ)שְׁמֹר",
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
caption = dmc.TableCaption("Conjugation of שמר in Paal")


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
