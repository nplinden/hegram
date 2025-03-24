from tf.app import use
from pathlib import Path
import pandas as pd

p = Path("data/conjugation.parquet")
p.parent.mkdir(exist_ok=True)
if not p.exists():
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
    conjugation = pd.DataFrame(data, columns=header)
    conjugation.to_parquet(p)


A = use("ETCBC/bhsa")
conjugation = pd.read_parquet(p)
