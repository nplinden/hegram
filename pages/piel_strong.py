import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/piel_strong")

layout = dmc.MantineProvider(
    [
        dash.html.Img(src="assets/piel_strong.svg", style={"width": "80%", "margin": "auto", "display": "block"}),
    ]
)
