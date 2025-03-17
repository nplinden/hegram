import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/niphal_strong")

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
        "Accompli": "נִקְדַּשְׁתִּי",
        "Inaccompli": "אֶקָּדֵשׁ, אִקָּדֵשׁ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MS",
        "Accompli": "נִקְדַּשְׁתָּ",
        "Inaccompli": "תִּקָּדֵשׁ",
        "Infinitif": "",
        "Impératif": "הִקָּדֵשׁ",
        "P. Présent": "",
    },
    {
        "Personne": "2FS",
        "Accompli": "נִקְדַּשְׁתְּ",
        "Inaccompli": "תִּקָּדְשִׁי",
        "Infinitif": "",
        "Impératif": "הִקׇּֽדְשִׁי",
        "P. Présent": "",
    },
    {
        "Personne": "3MS",
        "Accompli": "נִקְדַּשׁ",
        "Inaccompli": "יִקָּדֵשׁ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נִקְדָּשׁ",
    },
    {
        "Personne": "3FS",
        "Accompli": "נִקְדְּשָׁה",
        "Inaccompli": "תִּקָּדֵשׁ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נִקְדֶּשֶׁת",
    },
    {
        "Personne": "1P",
        "Accompli": "נִקְדַּשְׁנוּ",
        "Inaccompli": "נִקָּדֵֵשׁ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "2MP",
        "Accompli": "נִקְדַּשְׁתֶּם",
        "Inaccompli": "תִּקָּדְשׁוּ",
        "Infinitif": "",
        "Impératif": "הִקׇּֽדְשׁוּ",
        "P. Présent": "",
    },
    {
        "Personne": "2FP",
        "Accompli": "נִקְדַּשְׁתֶּן",
        "Inaccompli": "תִּקָּדֵשְׁנָה, תִּקָּדַשְׁנָה",
        "Infinitif": "",
        "Impératif": "הִקָּדֵשְׁנָה, הִקָּדַשְׁנָה",
        "P. Présent": "",
    },
    {
        "Personne": "3MP",
        "Accompli": "נִקְדְּשׁוּ",
        "Inaccompli": "יִקָּדְשׁוּ",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נִקְדָּשִׁים",
    },
    {
        "Personne": "3FP",
        "Accompli": "נִקְדְּשׁוּ",
        "Inaccompli": "תִּקָּדֵשְׁנָה, תִּקָּדַשְׁנָה",
        "Infinitif": "",
        "Impératif": "",
        "P. Présent": "נִקְדָּשׁוּת",
    },
    {
        "Personne": "Absolu",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "(לְ)הִקָּדֵשׁ",
        "Impératif": "",
        "P. Présent": "",
    },
    {
        "Personne": "Construit",
        "Accompli": "",
        "Inaccompli": "",
        "Infinitif": "נִקְדֹּשׁ, הִקָּדֹשׁ",
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
caption = dmc.TableCaption("Conjugation of קדש in Niphal")


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
