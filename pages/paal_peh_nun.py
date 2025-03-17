import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/paal_peh_nun")

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
        "Accompli": "נָפַ֫לְתִּי",
        "Inaccompli": "אֶפֹּל",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "נָפַ֫לְתָּ",
        "Inaccompli": "תִּפֹּל",
        "Infinitif": "",
        "Impératif": "נְפֹל",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "נָפַלְתְּ",
        "Inaccompli": "תִּפְּלִי",
        "Infinitif": "",
        "Impératif": "נִפְלִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "נָפַל",
        "Inaccompli": "יִפֹּל",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹפֵל",
    },
    {
        "Personne": "3FS",
        "Accompli": "נָֽפְלָה",
        "Inaccompli": "תִּפֹּל",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹפֶלֶת",
    },
    {
        "Personne": "1P",
        "Accompli": "נָפַ֫לְנוּ",
        "Inaccompli": "נִפֹּל",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "נְפַלְתֶּם",
        "Inaccompli": "תִּפְּלוּ",
        "Infinitif": "",
        "Impératif": "נִפְלוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "נְפַלְתֶּן",
        "Inaccompli": "תִּפֹּלְנָה",
        "Infinitif": "",
        "Impératif": "נְפֹלְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "נָֽפְלוּ",
        "Inaccompli": "יִפְּלוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹפְלִים",
    },
    {
        "Personne": "3FP",
        "Accompli": "נָֽפְלוּ",
        "Inaccompli": "תִּפֹּלְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹפְלוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "נָפוֹל",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "לִנְפֹּל",
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
caption = dmc.TableCaption("Conjugation of נפל in Paal")


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
