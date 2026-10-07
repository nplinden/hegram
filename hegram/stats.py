import polars as pl

from hegram.corpus import CONJUGATION
from hegram.data import COMMON_BINYANIM


def binyan_tense_counts(roots=None) -> list[dict]:
    """Occurrences of each tense per common binyan, as bar chart data.

    Args:
        roots: Restrict the count to these roots. Every root is counted when empty or None.
    """
    if not roots:
        return ALL_ROOTS_BINYAN_TENSE_COUNTS
    return _binyan_tense_counts(roots)


def _binyan_tense_counts(roots=None) -> list[dict]:
    df = CONJUGATION.filter(pl.col("Binyan").is_in(COMMON_BINYANIM))
    if roots:
        df = df.filter(pl.col("Root").is_in(roots))
    df = (
        df.select(["Binyan", "Tense"])
        .to_struct(name="Struct")
        .value_counts()
        .unnest("Struct")
        .sort("count", descending=True)
    )
    return df.pivot(["Tense"], index="Binyan", values="count").fill_null(0).to_dicts()


def _root_binyan_counts() -> pl.DataFrame:
    return (
        CONJUGATION.select(["Root", "Binyan"])
        .to_struct("Struct")
        .value_counts()
        .unnest("Struct")
        .pivot("Binyan", index="Root", values="count")
        .fill_null(0)
        .select(["Root"] + COMMON_BINYANIM)
        .with_columns(Total=pl.sum_horizontal(COMMON_BINYANIM))
        .sort("Total", descending=True)
        .filter(pl.col("Total") > 0)
    )


# The corpus never changes while the app runs, so the tables that don't depend on a selection are
# computed once. Callers must not modify them.

# Occurrences of each root per common binyan, plus a Total column, most frequent roots first.
ROOT_BINYAN_COUNTS = _root_binyan_counts()

# The binyan/tense chart over every root, the statistics page's default chart.
ALL_ROOTS_BINYAN_TENSE_COUNTS = _binyan_tense_counts()
