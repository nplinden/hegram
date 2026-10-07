import subprocess
import sys
from pathlib import Path

from flask import Flask
from loguru import logger
import dash_mantine_components as dmc
from dash import (
    Dash,
    _dash_renderer,
    html,
    dcc,
    page_registry,
    page_container,
    Output,
    Input,
    State,
    callback,
    ALL,
    callback_context,
)
from dash_iconify import DashIconify

_GENERATED_DATA = [
    "data/conjugation.parquet",
    "data/verses.parquet",
    "data/words.parquet",
    "data/definitions.json",
]
_missing = [f for f in _GENERATED_DATA if not Path(f).exists()]
if _missing:
    logger.error(
        "Missing generated data: {}. Build it first with "
        "`uv run --group build python -m hegram.build_dataframes` (see README).",
        ", ".join(_missing),
    )
    sys.exit(1)

_dash_renderer._set_react_version("18.2.0")
server = Flask("Hebrew Grammar")

app = Dash(
    __name__,
    title="Hegram",
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dmc.styles.CHARTS, dmc.styles.NOTIFICATIONS, dmc.styles.ALL],
)


@app.callback(
    Output({"type": "navlink", "index": ALL}, "active"),
    Input("_pages_location", "pathname"),
)
def update_navlinks(pathname):
    return [control["id"]["index"] == pathname for control in callback_context.outputs_list]


try:
    _commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
except (FileNotFoundError, subprocess.CalledProcessError):
    _commit = ""

# Sidebar menu. Top-level entries are (label, icon, target), nested entries are (label, target).
# A target is either a page module, which makes a link, or a list of entries, which makes a group.
NAV_MENU = [
    ("Statistiques", "material-symbols:bar-chart", "pages.statistics"),
    (
        "Exercices",
        "material-symbols:exercise",
        [
            ("Conjugaison", "pages.conjugation"),
            ("Prépositions", "pages.prepositions"),
            ("Nombres", "pages.numbers"),
        ],
    ),
    (
        "Conjugaison",
        "material-symbols:book-ribbon",
        [
            (
                "Paal",
                [
                    ("Verbe fort", "pages.paal_strong"),
                    ("Verbe פ’’נ", "pages.paal_peh_nun"),
                    ("Verbe פ’’יו", "pages.paal_peh_yodvav"),
                ],
            ),
            ("Piel", [("Verbe fort", "pages.piel_strong")]),
            (
                "Niphal",
                [
                    ("Verbe fort", "pages.niphal_strong"),
                    ("Verbe פ’’יו", "pages.niphal_peh_yodvav"),
                ],
            ),
            ("Poual", [("Verbe fort", "pages.poual_strong")]),
            ("Hiphil", [("Verbe fort", "pages.hiphil_strong")]),
            ("Hitpael", [("Verbe fort", "pages.hitpael_strong")]),
        ],
    ),
]


def nav_link(label, target, **props):
    if isinstance(target, str):
        path = page_registry[target]["relative_path"]
        # The id lets update_navlinks highlight the link of the current page.
        return dmc.NavLink(label=label, href=path, id={"type": "navlink", "index": path}, **props)
    return dmc.NavLink(label=label, childrenOffset=28, children=[nav_link(*entry) for entry in target], **props)


def nav_menu():
    return [
        nav_link(label, target, color="black", leftSection=DashIconify(icon=icon, height=16))
        for label, icon, target in NAV_MENU
    ]


app.layout = dmc.MantineProvider(
    dmc.AppShell(
        children=[
            dcc.Location(id="url", refresh=False),
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Burger(id="burger", size="sm", opened=False, hiddenFrom="sm"),
                                html.A(
                                    html.H1("Hegram by ניקולא לינדן", style={"textAlign": "center"}, id="title"),
                                    href="/",
                                ),
                            ]
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
            ),
            dmc.NotificationProvider(),
            html.Div(id="notification"),
            dmc.AppShellNavbar(
                children=[
                    *nav_menu(),
                    html.Div(
                        _commit,
                        style={"marginTop": "16px", "fontSize": "11px", "color": "#aaa"},
                    ),
                ],
                p="md",
            ),
            dmc.AppShellMain(children=[page_container]),
        ],
        padding="md",
        header={
            "height": 70,
            # "breakpoint": "sm",
            # "collapsed": {"mobile": False, "desktop": False},
            "collapsed": False,
        },
        navbar={
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"mobile": True, "desktop": False},
        },
        id="appshell",
    )
)


@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened, "desktop": False}
    return navbar


@callback(Output("burger", "opened"), Input("url", "pathname"))
def change_url(pathname):
    return False


if __name__ == "__main__":
    if sys.argv[-1] == "debug":
        app.run(
            debug=True,
            port=7777,
            dev_tools_hot_reload=True,
        )
    else:
        app.run(port=7777, host="0.0.0.0")
