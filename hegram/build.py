from hegram.data import binyanim_names, tense_names, common_binyanim
from hegram.utils import VerbRoot
from tf.app import use
import pandas as pd
from typing import Dict
import requests
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

hegram_path = Path("./data")
if not hegram_path.exists():
    hegram_path.mkdir(parents=True)


def get_occurences() -> pd.DataFrame:
    """Uses text-fabric and BHSA to build a dataframe of verb root occurence by
    binyanim and tenses. This saves the csv to ~/.local/share/hegram/occurences.csv
    If the file already exists, it is simply loaded instead or rebuilding the
    dataframe.

    Returns:
        pd.DataFrame: The dataframe of verb occurences
    """
    occurence_path = hegram_path / "occurences.csv"
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


osis = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
xml = "{http://www.w3.org/XML/1998/namespace}"


class Entry:
    def __init__(self, entry_node):
        w = entry_node.find(f"{osis}w")
        self.morph = w.attrib["morph"]
        if self.morph != "v":
            return
        self.root = w.text
        self.lang = w.attrib[f"{xml}lang"]

        self.definitions = []
        if (list_node := entry_node.find(f"{osis}list")) is not None:
            for def_node in list_node.findall(f"{osis}item"):
                self.definitions.append(def_node.text)
        self.definitions = [strong_to_markdown(self.definitions)]

def char_to_ordinal(ch: str):
    if ch.isdigit():
        return int(ch)
    else:
        return ord(ch) - 96

def strong_to_markdown(definition):
    full = ""
    for line in definition:
        print(line)
        try:
            level = re.match("(^[1-9a-z]+)\\)", line).groups()[0]
        except AttributeError:
            full += f"{line}\n"
            continue
        text = line.replace(f"{level}) ", "")
        levels = [char_to_ordinal(c) for c in level]
        depth = len(level)
        tabs = "".join(["\t" for _ in range(depth - 1)])
        tabs += f"{levels[-1]}. {text}"
        full += f"{tabs}\n"
    return full.strip()



def get_definitions() -> Dict:
    """Uses data from OpenScriptures to build a dictionnary of biblical hebrew
    words. This saves the csv to ~/.local/share/hegram/definitions.csv
    If the file already exists, it is simply loaded instead or rebuilding the
    dataframe.

    Returns:
        Dict: The dictionnary of word definitions
    """
    definitions_path = hegram_path / "definitions.json"
    if not definitions_path.exists():
        verbs = {}
        r = requests.get(
            "https://raw.githubusercontent.com/openscriptures/strongs/refs/heads/master/hebrew/StrongHebrewG.xml"
        )
        tree = ET.ElementTree(ET.fromstring(r.text))
        root = tree.getroot()
        osistext = root.findall(
            "{http://www.bibletechnologies.net/2003/OSIS/namespace}osisText"
        )[0]
        glossary = osistext.find(
            "{http://www.bibletechnologies.net/2003/OSIS/namespace}div"
        )
        for entry_node in glossary.findall(
            "{http://www.bibletechnologies.net/2003/OSIS/namespace}div"
        ):
            entry = Entry(entry_node)
            if entry.morph == "v" and entry.lang == "heb":
                if entry.root not in verbs:
                    verbs[entry.root] = [entry.definitions]
                else:
                    verbs[entry.root].append(entry.definitions)
        with open(definitions_path, "w") as f:
            json.dump(verbs, f, indent=2)
    else:
        with open(definitions_path, "r") as f:
            verbs = json.load(f)
    return verbs


df = get_occurences()
definitions = get_definitions()
