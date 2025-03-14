import pandas as pd
from tf.app import use
from pathlib import Path
from typing import List
import plotly.graph_objects as go
from hebrew import Hebrew


class VerbRoot:
    gutturals = "אהחע"

    def __init__(self, root):
        self.root = Hebrew(root).text_only()
        graphemes = list(self.root.graphemes)
        self.peh = graphemes[0]
        self.ayin = graphemes[1]
        self.lamed = graphemes[2]


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
        """Root-Binyan occurence series:

        Root  Binyan
        אבד   Hifil       26
              Paal       119
              Piel        41
        אבה   Paal        54
        אבך   Hitpael      1
                        ...
        תקן   Piel         2
        תקע   Nifal        3
              Paal        64
        תקף   Paal         3
        תרגם  Pual         1
        Name: Occurences, Length: 2869, dtype: int64

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
        return df

    def binyanim_bar_graph(
        self,
        radio,
        roots: List[str] = None,
    ):
        if roots is None:
            roots = self.roots

        if radio == "Binyan-Tense":
            ddf = self._df.reset_index()
            ddf = ddf[ddf["Root"].isin(roots)]
            ddf = ddf[~ddf["Binyan"].isin(self.uncommon_binyanim)]
            ddf = (
                ddf.drop(["Root"], axis=1)
                .groupby(["Binyan", "Tense"])
                .sum()
                .reset_index()
                .pivot_table(
                    values="Occurences",
                    index="Binyan",
                    columns=["Tense"],
                    aggfunc="sum",
                )
                .fillna(0)
            )
            ddf["Total"] = sum(ddf[c] for c in ddf.columns)
            print(ddf)
            ddf = ddf.sort_values(["Total"], ascending=False).reset_index()
            return ddf.to_dict("records")
        if radio == "Tense-Binyan":
            ddf = self._df.reset_index()
            ddf = ddf[ddf["Root"].isin(roots)]
            ddf = ddf[~ddf["Binyan"].isin(self.uncommon_binyanim)]
            ddf = (
                ddf.drop(["Root"], axis=1)
                .groupby(["Binyan", "Tense"])
                .sum()
                .reset_index()
                .pivot_table(
                    values="Occurences",
                    index="Tense",
                    columns=["Binyan"],
                    aggfunc="sum",
                )
                .fillna(0)
            )
            ddf["Total"] = sum(ddf[c] for c in ddf.columns)
            print(ddf)
            ddf = ddf.sort_values(["Total"], ascending=False).reset_index()
            return ddf.to_dict("records")
        if radio == "Binyan":
            ddf = self._df.reset_index()
            ddf = ddf[ddf["Root"].isin(roots)]
            ddf = ddf[~ddf["Binyan"].isin(self.uncommon_binyanim)]
            ddf = (
                ddf.drop(["Root", "Tense"], axis=1)
                .groupby(["Binyan"])
                .sum()
                .reset_index()
                .sort_values(["Occurences"], ascending=False)
            )
            return ddf.to_dict("records")
        if radio == "Tense":
            ddf = self._df.reset_index()
            ddf = ddf[ddf["Root"].isin(roots)]
            ddf = ddf[~ddf["Binyan"].isin(self.uncommon_binyanim)]
            ddf = (
                ddf.drop(["Root", "Binyan"], axis=1)
                .groupby(["Tense"])
                .sum()
                .reset_index()
                .sort_values(["Occurences"], ascending=False)
            )
            return ddf.to_dict("records")

    @property
    def roots(self) -> List[str]:
        """Get the list of all roots available

        Returns:
            List[str]: The list of roots
        """
        return sorted(list(self._df.index.levels[0]))


occurences = Occurences()
