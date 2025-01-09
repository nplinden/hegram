import pandas as pd
from tf.app import use
from pathlib import Path
from typing import List
import plotly.graph_objects as go
from dataclasses import dataclass
from hebrew import Hebrew


def strip_nikkud(word):
    return str(Hebrew(word).text_only())


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


class Occurences:
    bhsa_tenses = {
        "perf": "Qatal",
        "impf": "Yiqtol",
        "wayq": "Wayyiqtol",
        "impv": "Imperative",
        "infa": "Infinitive (abslute)",
        "infc": "Infinitive (construct)",
        "ptca": "Participle",
        "ptcp": "Participle (passive)",
    }
    bhsa_binyan = {
        "qal": "Paal",
        "piel": "Piel",
        "hif": "Hifil",
        "hit": "Hitpael",
        "hof": "Hofal",
        "pual": "Pual",
        "nif": "Nifal",
        "htpo": "Hitpoel",
        "poal": "Poal",
        "poel": "Poel",
        "afel": "Afel",
        "etpa": "Etpaal",
        "etpe": "Etpeel",
        "haf": "Hafel",
        "hotp": "Hotpaal",
        "hsht": "Hishtafal",
        "htpa": "Hitpaal",
        "htpe": "Hitpeel",
        "nit": "Nitpael",
        "pael": "Pael",
        "peal": "Peal",
        "peil": "Peil",
        "shaf": "Shafel",
        "tif": "Tifal",
        "pasq": "Passiveqal",
    }
    common_binyanim = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]
    #     uncommon_binyanim = ['Hitpoel',
    #  'Poal',
    #  'Poel',
    #  'Afel',
    #  'Etpaal',
    #  'Etpeel',
    #  'Hafel',
    #  'Hotpaal',
    #  'Hishtafal',
    #  'Hitpaal',
    #  'Hitpeel',
    #  'Nitpael',
    #  'Pael',
    #  'Peal',
    #  'Peil',
    #  'Shafel',
    #  'Tifal',
    #  'Passiveqal']

    def __init__(self):
        if Path("Occurences.csv").exists():
            self._df = pd.read_csv("Occurences.csv", index_col=[0, 1, 2], header=0)
        else:
            self._df = self.generate_occurences_df()
            self._df.to_csv("Occurences.csv")

    @classmethod
    def generate_occurences_df(cls) -> pd.DataFrame:
        A = use("ETCBC/bhsa")
        handles = {}
        A.hoist(handles)
        F = handles["F"]

        data = []
        for w in F.otype.s("word"):
            if F.sp.v(w) != "verb":
                continue
            if F.language.v(w) != "Hebrew":
                continue
            utf8 = str(Hebrew(F.lex_utf8.v(w)).text_only())
            stem = cls.bhsa_binyan[F.vs.v(w)]
            tense = cls.bhsa_tenses[F.vt.v(w)]
            data.append([utf8, stem, tense])
        df = pd.DataFrame(data, columns=["Root", "Binyan", "Tense"])
        series = df.groupby(["Root", "Binyan", "Tense"]).size()
        series.name = "Occurences"
        return series.to_frame()

    @property
    def uncommon_binyanim(self) -> List[str]:
        biynan_list = self._df.index.levels[1]
        return [b for b in biynan_list if b not in self.common_binyanim]

    def rbo(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Root-Binyan occurences.

        Args:
            remove_uncommon_binyanim (bool, optional): Whether to ommit very rare binyanim forms. Defaults to True.

        Returns:
            pd.Series: The series of occurences of root-binyan couples.
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=("Root", "Binyan"))
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=("Root", "Binyan")).sum()["Occurences"]

    def rbo_frame(
        self,
        total: bool = True,
        verb_class: bool = True,
        remove_uncommon_binyanim: bool = True,
    ) -> pd.DataFrame:
        df = (
            self.rbo(remove_uncommon_binyanim)
            .reset_index(level=1)
            .pivot_table("Occurences", ["Root"], ["Binyan"])
            .fillna(0)
            .convert_dtypes()
        )
        if total:
            df["Total"] = df.sum(axis=1)
            df = df.sort_values(["Total"], ascending=False)
            df["Rank"] = list(range(1, len(df) + 1))
        if verb_class:
            df["Class"] = [VerbRoot(r).root_class.hebrew for r in df.index]
        return df

    def rto(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Root-Tense occurences.

        Args:
            remove_uncommon_binyanim (bool, optional): Whether to ommit very rare binyanim forms. Defaults to True.

        Returns:
            pd.DataFrame: The series of occurences of root-tense couples
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=["Root", "Tense"])
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=["Root", "Tense"]).sum()["Occurences"]

    def binyanim_bar_graph(
        self, roots: List[str] = None, remove_uncommon_binyanim: bool = True
    ):
        if roots is None:
            roots = self.roots

        df = self.rbo_frame(True, False, remove_uncommon_binyanim).loc[roots]
        if len(df) == 1:
            title = f"Fréquence des Binyanim de {df.index[0]}"
        else:
            title = f"Fréquence des Binyanim pour {len(df)} racines"

        frequency = (df.sum() / df.sum()["Total"]).drop(["Total", "Rank"]).sort_values(
            ascending=False
        ) * 100
        text = [
            f"{f:d}"
            for f in df.sum().drop(["Rank", "Total"]).sort_values(ascending=False)
        ]

        fig = go.Figure(
            [
                go.Bar(
                    name="Frequency of Binyanim",
                    x=frequency.index,
                    y=frequency.values,
                    text=text,
                )
            ]
        )
        fig.update_layout(
            title=dict(text=title),
            xaxis=dict(title="Binyan"),
            yaxis=dict(title=r"Frequency (%)"),
        )
        return fig

    def bto(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Binyan-Tense occurences.

        Args:
            remove_uncommon_binyanim (bool, optional): Whether to ommit very rare binyanim forms. Defaults to True.

        Returns:
            pd.DataFrame: The series of occurences of binyan-tense couples
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=["Binyan", "Tense"])
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=["Binyan", "Tense"]).sum()["Occurences"]

    def ro(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Root occurences

        Returns:
            pd.DataFrame: The series of root occurences
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=["Root"])
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=["Root"]).sum()["Occurences"]

    def bo(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Binyan occurences

        Returns:
            pd.DataFrame: The series of binyan occurences
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=["Binyan"])
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=["Binyan"]).sum()["Occurences"]

    def to(self, remove_uncommon_binyanim: bool = True) -> pd.Series:
        """Tense occurences

        Returns:
            pd.DataFrame: The series of tense occurences
        """
        if remove_uncommon_binyanim:
            return (
                self._df.drop(self.uncommon_binyanim, level=1)
                .groupby(level=["Tense"])
                .sum()["Occurences"]
            )
        else:
            return self._df.groupby(level=["Tense"]).sum()["Occurences"]

    @property
    def roots(self) -> List[str]:
        """Get the list of all roots available

        Returns:
            List[str]: The list of roots
        """
        return sorted(list(self._df.index.levels[0]))


occurences = Occurences()
