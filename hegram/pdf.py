from html import escape
from pathlib import Path

import polars as pl
import weasyprint

from hegram.books import en_to_fr_books
from hegram.data import en_to_fr
from hegram.verses import build_verse_html, verse_words

_CSS = (Path(__file__).parent / "pdf.css").read_text(encoding="utf-8")


def verse_ref(verse_row: dict) -> str:
    book = en_to_fr_books[verse_row["book"]]
    return f"{book} {verse_row['chapter']}:{verse_row['verse']}"


def hebrew_numeral(n: int) -> str:
    if n <= 0:
        return str(n)

    ones = {1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט"}
    tens = {10: "י", 20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ"}
    hundreds = {100: "ק", 200: "ר", 300: "ש", 400: "ת"}

    letters = []

    while n >= 400:
        letters.append(hundreds[400])
        n -= 400

    for value in (300, 200, 100):
        if n >= value:
            letters.append(hundreds[value])
            n -= value

    if n == 15:
        letters.append("טו")
        n = 0
    elif n == 16:
        letters.append("טז")
        n = 0

    if n:
        for value in (90, 80, 70, 60, 50, 40, 30, 20, 10):
            if n >= value:
                letters.append(tens[value])
                n -= value
                break
        if n:
            letters.append(ones[n])

    raw = "".join(letters)
    if len(raw) == 1:
        return raw
    return raw


def sample_person_label(row: dict) -> str:
    number = {"Singular": "S", "Plural": "P"}.get(row.get("Number", ""), "")
    person = {"1": "1", "2": "2", "3": "3"}.get(str(row.get("Person", "")), "")
    gender = {"M": "M", "F": "F"}.get(row.get("Gender", ""), "")
    return f"{person}{gender}{number}" or "—"


def build_pdf_html(samples: list[dict], *, with_answers: bool = False) -> str:
    verse_ids = list({s["VerseId"] for s in samples})
    verses = {
        r["id"]: r
        for r in pl.scan_parquet("data/verses.parquet").filter(pl.col("id").is_in(verse_ids)).collect().to_dicts()
    }
    words = verse_words(list(verses.values()))
    answer_labels = ["Racine", "Binyan", "Temps", "Personne"]
    questions_html = ""
    for i, s in enumerate(samples, 1):
        verse_html = build_verse_html(verses[s["VerseId"]], words, s["WordId"])
        ref = verse_ref(verses[s["VerseId"]])
        if with_answers:
            answer_values = {
                "Racine": s["Root"],
                "Binyan": s["Binyan"],
                "Temps": en_to_fr["Tense"].get(s["Tense"], s["Tense"]),
                "Personne": sample_person_label(s),
            }
            answer_fields = "".join(
                f'<div class="answer-field">'
                f'<span class="answer-label">{label} :</span>'
                f'<span class="answer-value">{escape(str(answer_values[label]))}</span>'
                f"</div>"
                for label in answer_labels
            )
        else:
            answer_fields = "".join(
                f'<label class="answer-field" for="q{i}-{label.lower()}">'
                f'<span class="answer-label">{label} :</span>'
                f'<input class="answer-input" id="q{i}-{label.lower()}" name="q{i}-{label.lower()}" type="text" />'
                f"</label>"
                for label in answer_labels
            )
        qnum_he = hebrew_numeral(i)
        questions_html += f"""
<div class="question">
    <div class="question-number-he">{qnum_he}</div>
  <div class="cards-row">
    <div class="answer-section">{answer_fields}</div>
    <div class="verse-card">
      {verse_html}
      <div class="verse-ref">{ref}</div>
    </div>
  </div>
</div>"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Exercice de conjugaison</title>
<style>
{_CSS}</style>
</head>
<body>
{questions_html}
</body>
</html>"""


def render_pdf(samples: list[dict], *, with_answers: bool = False) -> bytes:
    """Render the conjugation worksheet, or its answer key, as PDF bytes.

    The questionnaire gets fillable form fields. The fonts are resolved against the assets folder.
    """
    html_content = build_pdf_html(samples, with_answers=with_answers)
    document = weasyprint.HTML(string=html_content, base_url=str(Path("assets").absolute()))
    return document.write_pdf(pdf_forms=not with_answers)
