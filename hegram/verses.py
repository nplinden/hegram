import polars as pl
from bs4 import BeautifulSoup, NavigableString

from hegram.corpus import WORDS

_HEBREW_CONSONANTS = set(chr(c) for c in range(0x05D0, 0x05EB))


def _hl(span):
    span["class"].append("hl")
    if span.string and span.string.endswith(" "):
        span.string.replace_with(span.string[:-1])
        span.insert_after(NavigableString(" "))


def verse_words(verse_rows: list[dict]) -> dict[int, str]:
    """Fetch the html of every word in the given verses, keyed by word id."""
    in_verses = pl.any_horizontal([pl.col("id").is_between(r["WordId_min"], r["WordId_max"]) for r in verse_rows])
    df = WORDS.filter(in_verses).select(["id", "html"])
    return dict(df.iter_rows())


def _verse_spans(verse_row: dict, words_html: dict[int, str], word_id: int) -> list[tuple]:
    """The verse's words as (span, highlighted) pairs. The verb is highlighted, and so is the word before
    it when that word is a single vav (the prefix of a wayyiqtol / waw-consecutive)."""
    # Rebuild the verse word by word rather than searching the verse html for the
    # verb's text: the same form can occur several times in a verse, and the verse
    # html sometimes merges several words into a single span.
    spans = []
    target = None
    for wid in range(verse_row["WordId_min"], verse_row["WordId_max"] + 1):
        span = BeautifulSoup(words_html[wid], features="html.parser").find("span")
        if span is None:  # word with no surface text, e.g. an elided article
            continue
        if wid == word_id:
            target = len(spans)
        spans.append(span)
    highlighted = {target}
    if target:  # the verb is not the first word
        consonants = [c for c in spans[target - 1].get_text() if c in _HEBREW_CONSONANTS]
        if consonants == ["ו"]:
            highlighted.add(target - 1)
    return [(span, i in highlighted) for i, span in enumerate(spans)]


def build_verse_html(verse_row: dict, words_html: dict[int, str], word_id: int) -> str:
    soup = BeautifulSoup('<div class="fullverse"></div>', features="html.parser")
    for span, highlighted in _verse_spans(verse_row, words_html, word_id):
        soup.div.append(span)
        if highlighted:
            _hl(span)
    return str(soup)


def verse_segments(verse_row: dict, words_html: dict[int, str], word_id: int) -> list[dict]:
    """The verse as plain-text segments, {"text": ..., "highlight": bool}, for the PDF worksheets.

    Consecutive words with the same highlighting are merged, and the space after a highlighted word
    is kept out of the highlight.
    """
    segments = []

    def add(text, highlight):
        if segments and segments[-1]["highlight"] == highlight:
            segments[-1]["text"] += text
        else:
            segments.append({"text": text, "highlight": highlight})

    for span, highlighted in _verse_spans(verse_row, words_html, word_id):
        text = span.get_text()
        if highlighted and text.endswith(" "):
            add(text[:-1], True)
            add(" ", False)
        else:
            add(text, highlighted)
    return segments
