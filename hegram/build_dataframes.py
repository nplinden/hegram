import json
import re
import xml.etree.ElementTree as ET

import polars as pl
import requests
from loguru import logger
from tf.app import use

STRONGS_URL = "https://raw.githubusercontent.com/openscriptures/strongs/refs/heads/master/hebrew/StrongHebrewG.xml"


def build_verses():
    A = use("ETCBC/bhsa")
    handles = {}
    A.hoist(handles)
    F = handles["F"]
    L = handles["L"]

    htmls = []
    for v in F.otype.s("verse"):
        html = A.plain(v, _asString=True, withPassage=False)
        section = A.sectionStrFromNode(v)
        book = section.split()[0]
        chapter, verse = section.split()[1].split(":")
        htmls.append([v, book, int(chapter), int(verse), html])
    df = pl.DataFrame(data=htmls, schema=["id", "book", "chapter", "verse", "html"], orient="row")

    data = []
    for w in F.otype.s("word"):
        verse_id = [u for u in L.u(w) if F.otype.v(u) == "verse"][0]
        data.append([w, verse_id])
    word_df = (
        pl.DataFrame(data=data, schema=["WordId", "VerseId"], orient="row")
        .group_by("VerseId")
        .agg([pl.col("WordId").min().name.suffix("_min"), pl.col("WordId").max().name.suffix("_max")])
        .sort("VerseId", descending=False)
    )
    complete = pl.concat([df, word_df], how="horizontal")
    complete.write_parquet("data/verses.parquet")


def build_conjugation():
    A = use("ETCBC/bhsa")
    handles = {}
    A.hoist(handles)
    F = handles["F"]
    L = handles["L"]
    T = handles["T"]

    binyanim = {
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

    tenses = {
        "perf": "Qatal",
        "impf": "Yiqtol",
        "wayq": "Wayyiqtol",
        "impv": "Imperative",
        "infa": "Infinitive (abslute)",
        "infc": "Infinitive (construct)",
        "ptca": "Participle",
        "ptcp": "Participle (passive)",
    }
    person = {"unknown": "None", "p1": "1", "p2": "2", "p3": "3"}
    gender = {"f": "F", "m": "M", "unknown": "None"}
    number = {"sg": "Singular", "pl": "Plural", "unknown": "None"}

    words = F.otype.s("word")
    verbs = [w for w in words if F.sp.v(w) == "verb"]

    header = [
        "WordId",
        "ClauseId",
        "VerseId",
        "Book",
        "Root",
        "Binyan",
        "Tense",
        "Person",
        "Gender",
        "Number",
        "Word",
    ]
    data = []
    for i in verbs:
        clause_id = [u for u in L.u(i) if F.otype.v(u) == "clause"][0]
        verse_id = [u for u in L.u(i) if F.otype.v(u) == "verse"][0]
        book_id = [u for u in L.u(i) if F.otype.v(u) == "book"][0]

        data.append(
            [
                i,
                clause_id,
                verse_id,
                T.bookName(book_id),
                F.lex_utf8.v(i),
                binyanim.get(F.vs.v(i), F.vs.v(i)),
                tenses.get(F.vt.v(i), F.vt.v(i)),
                person.get(F.ps.v(i), F.ps.v(i)),
                gender.get(F.gn.v(i), F.gn.v(i)),
                number.get(F.nu.v(i), F.nu.v(i)),
                F.g_word_utf8.v(i),
            ]
        )
    conjugation = pl.DataFrame(data, schema=header)
    conjugation.write_parquet("data/conjugation.parquet")


def build_words():
    A = use("ETCBC/bhsa")
    handles = {}
    A.hoist(handles)
    F = handles["F"]
    htmls = []
    for v in F.otype.s("word"):
        html = A.plain(v, _asString=True, withPassage=False)
        htmls.append([v, html])
    df = pl.DataFrame(data=htmls, schema=["id", "html"], orient="row")
    df.write_parquet("data/words.parquet")


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


def build_definitions():
    """Download the Strong's Hebrew dictionary from OpenScriptures and save its verb definitions,
    keyed by root, to data/definitions.json."""
    r = requests.get(STRONGS_URL, timeout=60)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    osistext = root.findall(f"{osis}osisText")[0]
    glossary = osistext.find(f"{osis}div")
    verbs = {}
    for entry_node in glossary.findall(f"{osis}div"):
        entry = Entry(entry_node)
        if entry.morph == "v" and entry.lang == "heb":
            verbs.setdefault(entry.root, []).append(entry.definitions)
    with open("data/definitions.json", "w", encoding="utf-8") as f:
        json.dump(verbs, f, indent=2)


if __name__ == "__main__":
    logger.info("Building data/verses.parquet")
    build_verses()
    logger.info("Building data/conjugation.parquet")
    build_conjugation()
    logger.info("Building data/words.parquet")
    build_words()
    logger.info("Building data/definitions.json")
    build_definitions()
    logger.info("Done")
