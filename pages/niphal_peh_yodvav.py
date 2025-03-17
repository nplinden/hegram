import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/niphal_peh_yodvav")

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
        "Accompli": "נוֹלַדְתִּי",
        "Inaccompli": "אִוָּלַד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "נוֹלַדְתָּ",
        "Inaccompli": "תִּוָּלֵד",
        "Infinitif": "",
        "Impératif": "הִוָּלֵד",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "נוֹלַדְתְּ",
        "Inaccompli": "תִּוָּֽלְדִי",
        "Infinitif": "",
        "Impératif": "הִוָּֽלְדִי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "נוֹלַד",
        "Inaccompli": "יִוָּלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹלָד",
    },
    {
        "Personne": "3FS",
        "Accompli": "נוֹלְדָה",
        "Inaccompli": "תִּוָּלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹלֶדֶת, נוּלָדָה",
    },
    {
        "Personne": "1P",
        "Accompli": "נוֹלַדְנוּ",
        "Inaccompli": "נִוָּלֵד",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "נוֹלַדְתֶּם",
        "Inaccompli": "תִּוָּֽלְדוּ",
        "Infinitif": "",
        "Impératif": "הֹוָּֽלְדוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "נוֹלַדְתֶּן",
        "Inaccompli": "תִּוָּלַדְנָה",
        "Infinitif": "",
        "Impératif": "הִוָּלֵדְנָה, הִוָּלַדְנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "נוֹלְדוּ",
        "Inaccompli": "יִוָּֽלְדוּ",
        "Infinitif": "",
        "Impératif": "נוֹלָדִים",
        "P. Présent": "",
    },
    {
        "Personne": "3FP",
        "Accompli": "נוֹלְדוּ",
        "Inaccompli": "תִּוָּלַדְנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נוֹלָדוֹת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "נוֹלוֹד",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "הִוָּלֵד",
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
caption = dmc.TableCaption("Conjugation of ילד in Niphal")


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
