import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
from typing import List
from hegram.data import tense_names, common_binyanim
from hebrew import Hebrew
from dataclasses import dataclass


@dataclass
class RootClass:
    """Class for storing root class names"""

    hebrew: str
    latin: str


class VerbRoot:
    gutturals = "אהחע"

    def __init__(self, root):
        self.root = Hebrew(root).text_only()
        graphemes = list(self.root.graphemes)
        self.peh = graphemes[0]
        self.ayin = graphemes[1]
        self.lamed = graphemes[2]

        if self.peh == "א":
            self.root_class = RootClass("פ׳׳א", "peh-aleph")
        elif self.peh in "וי":
            self.root_class = RootClass("פ׳׳וי", "peh-vav[yod]")
        elif self.peh == "נ":
            self.root_class = RootClass("פ׳׳נ", "peh-nun")
        elif self.ayin in "וי":
            self.root_class = RootClass("ע׳׳וי", "ayin-vav[yod]")
        elif self.ayin == self.lamed:
            self.root_class = RootClass("ע׳׳ע", "Géminé")
        elif self.lamed == "א":
            self.root_class = RootClass("ל׳׳א", "lamed-aleph")
        elif self.lamed == "ה":
            self.root_class = RootClass("ל׳׳ה", "lamed-he")
        elif self.peh in self.gutturals:
            self.root_class = RootClass("פ׳׳ג", "peh-gutturale")
        elif self.ayin in self.gutturals:
            self.root_class = RootClass("ע׳׳ג", "ayin-gutturale")
        elif self.lamed in self.gutturals:
            self.root_class = RootClass("ל׳׳ג", "lamed-gutturale")
        else:
            self.root_class = RootClass("Fort", "Fort")


def binyanim_freq(
    df: pd.DataFrame, roots: List[str] = None, threshold: int = None
) -> go.Figure:
    """This creates a plotly bar graph of binyanim frequency given a dataframe
    generated from BHSA data.

    Args:
        df (pd.DataFrame): A dataframe of binyanim and tense occurrences
        roots (List[str], optional): A list of verb root to restrict the analysis to. Defaults to None.
        threshold (int, optional): A threshold of frequency rank to restrict the analysis to. Defaults to None.

    Raises:
        ValueError: Both the roots and threshold parameters can't be provided at the same time

    Returns:
        go.Figure: A bar graph of binyanim frequency
    """
    _df = df.drop(tense_names.values(), axis=1).drop("Classe", axis=1)
    if roots is not None and threshold is not None:
        raise ValueError("can't provide both roots list and threshold")
    if roots is not None:
        _roots = [r for r in roots if r in _df.index]
        _df = _df.loc[_roots]
    if len(_df) > 1:
        title = f"Fréquence des Binyanim pour {len(_df)} racines"
    else:
        title = f"Fréquence des Binyanim de {_df.index[0]}"

    # if threshold is not None:
    #     _df = _df[_df.Rank <= threshold]
    #     title = f"Fréquence de binyanim pour les {threshold} racines les plus courantes"

    freq = (_df.sum() / _df.sum()["Total"]).drop(
        ["Rank", "Common", "Total"]
    ).sort_values(ascending=False) * 100
    text = [
        f"{f:d}"
        for f in _df.sum()
        .drop(["Rank", "Common", "Total"])
        .sort_values(ascending=False)
    ]

    fig = go.Figure(
        [
            go.Bar(
                name="Frequency of binyanim",
                x=freq.index,
                y=freq.values,
                text=text,
            )
        ],
    )
    fig.update_layout(
        title=dict(text=title),
        xaxis=dict(title="Nom du Binyan"),
        yaxis=dict(title=r"Fréquence (%)"),
    )
    return fig


def tense_freq(
    df: pd.DataFrame, roots: List[str] = None, threshold: int = None
) -> go.Figure:
    _df = df.drop(common_binyanim, axis=1)
    if roots is not None and threshold is not None:
        raise ValueError("can't provide both roots list and threshold")
    if roots is not None:
        _df = _df.loc[roots]
    title = "Fréquence des conjugaisons"
    if threshold is not None:
        _df = _df[_df.Rank <= threshold]
        title = (
            f"Fréquence de conjugaisons pour les {threshold} racines les plus courantes"
        )
    _df = _df.drop(["Rank", "Common", "Uncommon", "Classe"], axis=1)

    tense_frequency = (_df.sum() / _df.sum()["Total"]).drop(["Total"]).sort_values(
        ascending=False
    ) * 100
    tense_text = [f"{f:.1f}" for f in tense_frequency]
    tense_fig = go.Figure(
        [
            go.Bar(
                name="Fréquence des conjugaisons",
                x=tense_frequency.index,
                y=tense_frequency.values,
                text=tense_text,
            )
        ],
    )
    tense_fig.update_layout(
        title=dict(text=title),
        xaxis=dict(title="Conjugaison"),
        yaxis=dict(title=r"Fréquence (%)"),
    )
    return tense_fig


def root_table_data(df: pd.DataFrame, roots: List[str] = None, threshold: int = None):
    _df = df.drop(tense_names.values(), axis=1).reset_index(names=["Racine"])[
        ["Rank", "Racine", "Total", "Classe"]
    ]
    if roots is not None:
        _df = _df[_df.Racine.isin(roots)]
    cols = [{"name": i, "id": i} for i in _df.columns]
    return _df.to_dict("records"), cols
