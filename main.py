import sys
from flask import Flask
import dash_mantine_components as dmc
from dash import (
    Dash,
    _dash_renderer,
    html,
    page_registry,
    page_container,
    Output,
    Input,
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
    url_base_pathname="/hegram/",
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

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        children=[
            dmc.NotificationProvider(),
            html.Div(id="notification"),
            dmc.AppShellNavbar(
                children=[
                    html.H1("Hegram by ניקולא לינדן", style={"textAlign": "center"}),
                    dmc.NavLink(
                        label="Statistiques",
                        href=page_registry["pages.statistics"]["relative_path"],
                        id={"type": "navlink", "index": page_registry["pages.statistics"]["relative_path"]},
                        leftSection=DashIconify(icon="material-symbols:bar-chart", height=16),
                    ),
                    dmc.NavLink(
                        label="Exercices",
                        href=page_registry["pages.conjugation"]["relative_path"],
                        id={"type": "navlink", "index": page_registry["pages.conjugation"]["relative_path"]},
                        leftSection=DashIconify(icon="material-symbols:exercise", height=16),
                    ),
                    dmc.NavLink(
                        label="Ressources",
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
                                        label="פ’’נ Verb",
                                        href=page_registry["pages.paal_peh_nun"]["relative_path"],
                                        id={
                                            "type": "navlink",
                                            "index": page_registry["pages.paal_peh_nun"]["relative_path"],
                                        },
                                    ),
                                    dmc.NavLink(
                                        label="פ’’יו Verb",
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
                                        label="פ’’יו",
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
                        ],
                    ),
                ],
                p="md",
            ),
            dmc.AppShellMain(children=[page_container]),
        ],
        padding="md",
        navbar={
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
    )
)

if __name__ == "__main__":
    if sys.argv[-1] == "debug":
        app.run_server(
            debug=True,
            port=7777,
            dev_tools_hot_reload=True,
        )
    else:
        app.run_server(port=7777, host="0.0.0.0")
