"""Conjugation worksheets as PDF, rendered with Typst from worksheet.typ."""

import json
from pathlib import Path

import polars as pl
import typst

from hegram.books import en_to_fr_books
from hegram.corpus import VERSES
from hegram.data import en_to_fr
from hegram.verses import verse_segments, verse_words

_TEMPLATE = Path(__file__).parent / "worksheet.typ"
# Ezra SIL as TTF: Typst can't read the WOFF the web pages use. Latin fonts come from the system.
_FONTS = Path(__file__).parent / "fonts"


def verse_ref(verse_row: dict) -> str:
    book = en_to_fr_books[verse_row["book"]]
    return f"{book} {verse_row['chapter']}:{verse_row['verse']}"


def sample_person_label(row: dict) -> str:
    number = {"Singular": "S", "Plural": "P"}.get(row.get("Number", ""), "")
    person = {"1": "1", "2": "2", "3": "3"}.get(str(row.get("Person", "")), "")
    gender = {"M": "M", "F": "F"}.get(row.get("Gender", ""), "")
    return f"{person}{gender}{number}" or "—"


def worksheet_data(samples: list[dict], *, with_answers: bool = False) -> dict:
    """The data worksheet.typ renders: one question per sampled verb."""
    verse_ids = list({s["VerseId"] for s in samples})
    verses = {r["id"]: r for r in VERSES.filter(pl.col("id").is_in(verse_ids)).to_dicts()}
    words = verse_words(list(verses.values()))
    questions = []
    for s in samples:
        verse = verses[s["VerseId"]]
        answers = {
            "Racine": s["Root"],
            "Binyan": s["Binyan"],
            "Temps": en_to_fr["Tense"].get(s["Tense"], s["Tense"]),
            "Personne": sample_person_label(s),
        }
        questions.append(
            {
                "segments": verse_segments(verse, words, s["WordId"]),
                "ref": verse_ref(verse),
                "fields": [
                    {"label": label, "value": value if with_answers else "", "hebrew": label == "Racine"}
                    for label, value in answers.items()
                ],
            }
        )
    return {"answers": with_answers, "questions": questions}


def render_pdf(samples: list[dict], *, with_answers: bool = False) -> bytes:
    """Render the conjugation worksheet, or its answer key, as PDF bytes."""
    data = worksheet_data(samples, with_answers=with_answers)
    return typst.compile(str(_TEMPLATE), font_paths=[str(_FONTS)], sys_inputs={"data": json.dumps(data)})
