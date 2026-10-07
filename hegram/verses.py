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


def build_verse_html(verse_row: dict, words_html: dict[int, str], word_id: int) -> str:
    # Rebuild the verse word by word rather than searching the verse html for the
    # verb's text: the same form can occur several times in a verse, and the verse
    # html sometimes merges several words into a single span.
    soup = BeautifulSoup('<div class="fullverse"></div>', features="html.parser")
    prev = target = None
    for wid in range(verse_row["WordId_min"], verse_row["WordId_max"] + 1):
        span = BeautifulSoup(words_html[wid], features="html.parser").find("span")
        if span is None:  # word with no surface text, e.g. an elided article
            continue
        soup.div.append(span)
        if wid < word_id:
            prev = span
        elif wid == word_id:
            target = span
    _hl(target)
    if prev is not None:
        consonants = [c for c in prev.get_text() if c in _HEBREW_CONSONANTS]
        if consonants == ["\u05d5"]:  # single vav — prefix of wayyiqtol/waw-consecutive
            _hl(prev)
    return str(soup)
