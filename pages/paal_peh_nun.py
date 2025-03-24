import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/paal_peh_nun")

layout = dmc.MantineProvider(
    [
        dash.html.Img(src="assets/paal_peh_nun.svg", style={"width": "80%", "margin": "auto", "display": "block"}),
    ]
)
