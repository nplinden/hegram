import polars as pl

COMMON_BINYANIM = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]


def binyan_tense_counts(roots=None) -> list[dict]:
    """Occurrences of each tense per common binyan, as bar chart data.

    Args:
        roots: Restrict the count to these roots. Every root is counted when empty or None.
    """
    df = pl.scan_parquet("data/conjugation.parquet").filter(pl.col("Binyan").is_in(COMMON_BINYANIM))
    if roots:
        df = df.filter(pl.col("Root").is_in(roots))
    df = (
        df.select(["Binyan", "Tense"])
        .collect()
        .to_struct(name="Struct")
        .value_counts()
        .unnest("Struct")
        .sort("count", descending=True)
    )
    return df.pivot(["Tense"], index="Binyan", values="count").fill_null(0).to_dicts()


def _root_binyan_counts() -> pl.DataFrame:
    return (
        pl.scan_parquet("data/conjugation.parquet")
        .select(["Root", "Binyan"])
        .collect()
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


# Occurrences of each root per common binyan, plus a Total column, most frequent roots first.
# The corpus never changes while the app runs, so this is computed once.
ROOT_BINYAN_COUNTS = _root_binyan_counts()
