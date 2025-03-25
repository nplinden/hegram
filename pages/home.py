import dash
import dash_mantine_components as dmc
from dash import html

dash.register_page(__name__, path="/")

layout = dmc.MantineProvider(
    [
        html.H1("Bienvenue sur Hegram !"),
        html.P("Hegram est un site dédié à l'apprentissage et à l'exploration de l'Hébreu biblique."),
        html.P("Il existe pour l'instant trois sections sur le site :"),
        html.Ul(
            children=[
                html.Li(
                    "Une section « statistique » où vous pourrez trouver des informations sur la fréquence d'occurrence de toutes les racines verbales présente dans la Bible Hébraïque."
                ),
                html.Li(
                    "Une section « exercice » permettant de générer aléatoirement des exercices de conjugaison, à destination des apprenants."
                ),
                html.Li("Une section « ressources » contenant des aide-mémoire grammaticaux."),
            ]
        ),
        html.P("Ces sections sont accessibles depuis le menu latéral."),
        html.H1("Sources"),
        html.P(
            children=[
                "Les interactions avec le corpus biblique sont faites au moyen de la ",
                html.A(
                    children=["Hebrew Bible Database"], href="https://doi.org/10.17026/dans-z6y-skyh", className="link"
                ),
                ", compilé par le ",
                html.Em("Eep Talstra Centre for Bible and Computer, VU University Amsterdam"),
                ".",
            ]
        ),
        html.P(
            children=[
                "Les définitions sont issues du dépôt GitHub ",
                html.A("openscriptures/strongs", href="https://github.com/openscriptures/strongs/", className="link"),
                ".",
            ]
        ),
    ]
)
