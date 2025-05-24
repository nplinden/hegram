import sys
from flask import Flask
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

_dash_renderer._set_react_version("18.2.0")
server = Flask("Hebrew Grammar")

app = Dash(
    __name__,
    title="Hegram",
    server=server,
    use_pages=True,
    external_stylesheets=[dmc.styles.CHARTS, dmc.styles.NOTIFICATIONS, dmc.styles.ALL],
)


@app.callback(
    Output({"type": "navlink", "index": ALL}, "active"),
    Input("_pages_location", "pathname"),
)
def update_navlinks(pathname):
    return [control["id"]["index"] == pathname for control in callback_context.outputs_list]


icons = {
    "Conjugation": DashIconify(icon="material-symbols:exercise", height=16),
    "Statistics": DashIconify(icon="material-symbols:bar-chart", height=16),
    "Learning": DashIconify(icon="material-symbols:book-ribbon", height=16),
}

buttons = [
    dmc.Button("Home", variant="subtle", color="gray"),
    dmc.Button("Blog", variant="subtle", color="gray"),
    dmc.Button("Contacts", variant="subtle", color="gray"),
    dmc.Button("Support", variant="subtle", color="gray"),
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
                    # html.H1("Hegram by ניקולא לינדן", id="title"),
                    dmc.NavLink(
                        label="Statistiques",
                        color="black",
                        href=page_registry["pages.statistics"]["relative_path"],
                        id={"type": "navlink", "index": page_registry["pages.statistics"]["relative_path"]},
                        leftSection=DashIconify(icon="material-symbols:bar-chart", height=16),
                    ),
                    dmc.NavLink(
                        label="Exercices",
                        color="black",
                        href=page_registry["pages.conjugation"]["relative_path"],
                        id={"type": "navlink", "index": page_registry["pages.conjugation"]["relative_path"]},
                        leftSection=DashIconify(icon="material-symbols:exercise", height=16),
                    ),
                    dmc.NavLink(
                        label="Conjugaison",
                        color="black",
                        leftSection=DashIconify(icon="material-symbols:book-ribbon", height=16),
                        childrenOffset=28,
                        children=[
                            dmc.NavLink(
                                label="Paal",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.paal_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.paal_strong"]["relative_path"],
                                        },
                                    ),
                                    dmc.NavLink(
                                        label="Verbe פ’’נ",
                                        href=page_registry["pages.paal_peh_nun"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.paal_peh_nun"]["relative_path"],
                                        },
                                    ),
                                    dmc.NavLink(
                                        label="Verbe פ’’יו",
                                        href=page_registry["pages.paal_peh_yodvav"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.paal_peh_yodvav"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                            dmc.NavLink(
                                label="Piel",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.piel_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.piel_strong"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                            dmc.NavLink(
                                label="Niphal",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.niphal_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.niphal_strong"]["relative_path"],
                                        },
                                    ),
                                    dmc.NavLink(
                                        label="Verbe פ’’יו",
                                        href=page_registry["pages.niphal_peh_yodvav"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.niphal_peh_yodvav"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                            dmc.NavLink(
                                label="Poual",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.poual_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.poual_strong"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                            dmc.NavLink(
                                label="Hiphil",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.hiphil_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.hiphil_strong"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                            dmc.NavLink(
                                label="Hitpael",
                                childrenOffset=28,
                                children=[
                                    dmc.NavLink(
                                        label="Verbe fort",
                                        href=page_registry["pages.hitpael_strong"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.hitpael_strong"]["relative_path"],
                                        },
                                    ),
                                ],
                            ),
                        ],
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
        app.run_server(
            debug=True,
            port=7777,
            dev_tools_hot_reload=True,
        )
    else:
        app.run(port=7777, host="0.0.0.0")
