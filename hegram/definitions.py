from typing import Dict
import requests
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

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
    """
    Converts a character to its corresponding ordinal value, where digits are
    converted to their integer form and alphabetic characters are converted
    to their positional value in the alphabet (a=1, b=2, ..., z=26).

    Args:
        ch (str): Input character. Can be a digit or an alphabetic character.

    Returns:
        int: The integer equivalent of the input character - either the digit
        itself or the positional value in the alphabet for alphabetic input.
    """
    if ch.isdigit():
        return int(ch)
    else:
        return ord(ch) - 96


def strong_to_markdown(definition):
    full = ""
    for line in definition:
        # print(line)
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
    p = Path("data/definitions.json")
    p.parent.mkdir(exist_ok=True)
    if not p.exists():
        verbs = {}
        r = requests.get(
            "https://raw.githubusercontent.com/openscriptures/strongs/refs/heads/master/hebrew/StrongHebrewG.xml"
        )
        tree = ET.ElementTree(ET.fromstring(r.text))
        root = tree.getroot()
        osistext = root.findall("{http://www.bibletechnologies.net/2003/OSIS/namespace}osisText")[0]
        glossary = osistext.find("{http://www.bibletechnologies.net/2003/OSIS/namespace}div")
        for entry_node in glossary.findall("{http://www.bibletechnologies.net/2003/OSIS/namespace}div"):
            entry = Entry(entry_node)
            if entry.morph == "v" and entry.lang == "heb":
                if entry.root not in verbs:
                    verbs[entry.root] = [entry.definitions]
                else:
                    verbs[entry.root].append(entry.definitions)
        with open(p, "w") as f:
            json.dump(verbs, f, indent=2)
    else:
        with open(p, "r") as f:
            verbs = json.load(f)
    return verbs


definitions = get_definitions()
