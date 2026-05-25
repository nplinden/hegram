import dash
import dash_mantine_components as dmc
from dash import dcc, Input, Output, callback, html
from dash_iconify import DashIconify

dash.register_page(__name__, path="/paal_strong")

_ACCOMPLI = [
    ("1S",  "שָׁמַרְתִּי"), ("2MS", "שָׁמַרְתָּ"),  ("2FS", "שָׁמַרְתְּ"),
    ("3MS", "שָׁמַר"),      ("3FS", "שָׁמְרָה"),    ("1P",  "שָׁמַרְנוּ"),
    ("2MP", "שָׁמַרְתֶּם"), ("2FP", "שָׁמַרְתֶּן"), ("3MP", "שָׁמְרוּ"),
    ("3FP", "שָׁמְרוּ"),
]
_INACCOMPLI = [
    ("1S",  "אֶשְׁמֹר"),   ("2MS", "תִּשְׁמֹר"),   ("2FS", "תִּשְׁמְרִי"),
    ("3MS", "יִשְׁמֹר"),   ("3FS", "תִּשְׁמֹר"),   ("1P",  "נִשְׁמֹר"),
    ("2MP", "תִּשְׁמְרוּ"), ("2FP", "תִּשְׁמֶרְנָה"), ("3MP", "יִשְׁמְרוּ"),
    ("3FP", "תִּשְׁמֶרְנָה"),
]
_IMPERATIF = [
    ("2MS", "שְׁמֹר"), ("2FS", "שִׁמְרִי"), ("2MP", "שִׁמְרוּ"), ("2FP", "שִׁמֶרְנָה"),
]
_PARTICIPE = [
    ("MS", "שׁוֹמֵר"), ("FS", "שׁוֹמֶרֶת"), ("MP", "שׁוֹמְרִים"), ("FP", "שׁוֹמְרוֹת"),
]

_CARD_STYLE = {
    "borderRadius": "16px",
    "border": "1px solid #e0e0e0",
    "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
    "overflow": "hidden",
    "backgroundColor": "#FFFFFF",
}

_HEADER_STYLE = {
    "padding": "12px 20px",
    "backgroundColor": "#F8F9FA",
    "borderBottom": "1px solid #e0e0e0",
}

_ROW_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "padding": "6px 20px",
    "gap": "16px",
    "borderBottom": "1px solid rgba(0,0,0,0.05)",
}

_HEB_STYLE = {
    "fontFamily": '"Ezra SIL", sans-serif',
    "fontSize": "1.8rem",
    "direction": "rtl",
    "textAlign": "right",
    "margin": 0,
    "flex": 1,
}


def _conj_card(title, pairs):
    rows = [
        html.Div(
            [
                dmc.Text(person, size="sm", c="dimmed", style={"minWidth": "40px", "flexShrink": 0}),
                html.P(form, style=_HEB_STYLE),
            ],
            style=_ROW_STYLE,
        )
        for person, form in pairs
    ]
    return html.Div(
        [
            html.Div(dmc.Text(title, fw=600, size="md"), style=_HEADER_STYLE),
            *rows,
        ],
        style=_CARD_STYLE,
    )


def _single_card(title, form):
    return html.Div(
        [
            html.Div(dmc.Text(title, fw=600, size="md"), style=_HEADER_STYLE),
            html.Div(
                html.P(form, style={**_HEB_STYLE, "fontSize": "2.5rem", "textAlign": "center"}),
                style={"padding": "20px 20px", "textAlign": "center"},
            ),
        ],
        style=_CARD_STYLE,
    )


layout = dmc.MantineProvider(
    html.Div(
        [
            dcc.Download(id="download-paal-strong"),
            dmc.Flex(
                [
                    html.Div(
                        [
                            html.P(
                                "שׁמר",
                                style={
                                    "fontFamily": '"Ezra SIL", sans-serif',
                                    "fontSize": "2.5rem",
                                    "direction": "rtl",
                                    "margin": "0 0 2px 0",
                                    "lineHeight": 1.2,
                                },
                            ),
                            dmc.Text("Verbe fort au Paal", size="sm", c="dimmed"),
                        ]
                    ),
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:download", width=20),
                        id="button-paal-strong",
                        variant="subtle",
                        color=dmc.DEFAULT_THEME["colors"]["dark"][6],
                        size="lg",
                    ),
                ],
                justify="space-between",
                align="center",
                mb=24,
            ),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2},
                spacing="lg",
                mb=16,
                children=[
                    _single_card("Infinitif absolu",   "שָׁמוֹר"),
                    _single_card("Infinitif construit", "(לִ)שְׁמֹר"),
                ],
            ),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2},
                spacing="lg",
                mb=16,
                children=[
                    _conj_card("Accompli",   _ACCOMPLI),
                    _conj_card("Inaccompli", _INACCOMPLI),
                ],
            ),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2},
                spacing="lg",
                children=[
                    _conj_card("Impératif",       _IMPERATIF),
                    _conj_card("Participe présent", _PARTICIPE),
                ],
            ),
        ],
        className="container",
    )
)


@callback(
    Output("download-paal-strong", "data"),
    Input("button-paal-strong", "n_clicks"),
    prevent_initial_call=True,
)
def download_pdf(_):
    return dcc.send_file("assets/paal_strong.svg")
