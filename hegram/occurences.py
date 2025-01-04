from hegram.data import binyanim_names, tense_names, common_binyanim
from hegram.utils import VerbRoot
from tf.app import use
import pandas as pd
from hegram.env import data_path


def get_occurences() -> pd.DataFrame:
    """Uses text-fabric and BHSA to build a dataframe of verb root occurence by
    binyanim and tenses. This saves the csv to ~/.local/share/hegram/occurences.csv
    If the file already exists, it is simply loaded instead or rebuilding the
    dataframe.

    Returns:
        pd.DataFrame: The dataframe of verb occurences
    """
    occurence_path = data_path / "occurences.csv"
    if not occurence_path.exists():
        A = use("ETCBC/bhsa", hoist=globals())
        handles = {}
        A.hoist(handles)
        F = handles["F"]

        binyan_dict = {}
        translations = {}
        tenses_dict = {}
        for w in F.otype.s("word"):
            if F.sp.v(w) != "verb":
                continue
            if F.language.v(w) != "Hebrew":
                continue
            utf8 = F.lex_utf8.v(w)
            stem = binyanim_names[F.vs.v(w)]
            gloss = F.gloss.v(w)
            tense = tense_names[F.vt.v(w)]

            if utf8 not in binyan_dict:
                binyan_dict[utf8] = {}
            if stem not in binyan_dict[utf8]:
                binyan_dict[utf8][stem] = 0
            binyan_dict[utf8][stem] += 1
            if utf8 not in translations:
                translations[utf8] = set()
            translations[utf8].add(gloss)

            if utf8 not in tenses_dict:
                tenses_dict[utf8] = {}
            if tense not in tenses_dict[utf8]:
                tenses_dict[utf8][tense] = 0
            tenses_dict[utf8][tense] += 1

        binyan = pd.DataFrame(data=binyan_dict).T.fillna(0).convert_dtypes()
        uncommon = [u for u in binyan.columns if u not in common_binyanim]
        binyan["Total"] = binyan.sum(axis=1)
        binyan["Common"] = binyan[common_binyanim].sum(axis=1)
        binyan["Uncommon"] = binyan[uncommon].sum(axis=1)
        binyan = binyan.drop(uncommon, axis=1).sort_values(by="Total", ascending=False)
        binyan["Rank"] = [i + 1 for i in range(len(binyan))]

        tenses = (pd.DataFrame(data=tenses_dict).T.fillna(0).convert_dtypes())[
            tense_names.values()
        ]
        tenses["Total"] = tenses.sum(axis=1)
        tenses = tenses.sort_values(by="Total", ascending=False)
        tenses["Rank"] = [i + 1 for i in range(len(tenses))]

        df = pd.concat([binyan, tenses.drop(["Total", "Rank"], axis=1)], axis=1)
        df["Classe"] = [VerbRoot(i).root_class.hebrew for i in df.index]
        df.to_csv(occurence_path, index=True)
    else:
        df = pd.read_csv(occurence_path, index_col=0)
    return df


df = get_occurences()
