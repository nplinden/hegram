import dash
import dash_mantine_components as dmc


dash.register_page(__name__, path="/niphal_peh_yodvav")

layout = dmc.MantineProvider(
    [
        dash.html.Img(src="assets/niphal_peh_yodvav.svg", style={"width": "80%", "margin": "auto", "display": "block"}),
    ]
)
