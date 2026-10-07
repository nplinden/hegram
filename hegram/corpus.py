"""The corpus tables built by hegram.build_dataframes, loaded once into memory when the app starts.

They are small (about 60 MB in memory) and never change while the app runs, so callbacks filter
these frames instead of reading the parquet files on every request.
"""

import polars as pl

from hegram.paths import DATA_DIR

# One row per verb occurrence: WordId, VerseId, Book, Root, Binyan, Tense, Person, Gender, Number…
CONJUGATION = pl.read_parquet(DATA_DIR / "conjugation.parquet")
# One row per verse: id, book, chapter, verse, html, WordId_min, WordId_max.
VERSES = pl.read_parquet(DATA_DIR / "verses.parquet")
# One row per word: id, html.
WORDS = pl.read_parquet(DATA_DIR / "words.parquet")


def verse_row(verse_id: int) -> dict:
    return VERSES.row(by_predicate=pl.col("id") == verse_id, named=True)


def word_row(word_id: int) -> dict:
    return WORDS.row(by_predicate=pl.col("id") == word_id, named=True)
