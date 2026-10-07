A webapp for analysing binyanim and tenses occurrence in the Hebrew Bible.

This mostly exists as a personal learning project for Plotly's dash.

# Running Hegram

You need [uv](https://github.com/astral-sh/uv) to run Hegram.

## 1. Build the data

The corpus data is not versioned and must be generated once after cloning:

```bash
git clone https://github.com/nplinden/hegram.git
cd hegram
uv run python -m hegram.build_dataframes
```

This produces:

| File | Content | Source |
|---|---|---|
| `data/conjugation.parquet` | every verb occurrence with its root, binyan, tense, person, gender and number | [BHSA](https://github.com/ETCBC/bhsa) |
| `data/verses.parquet` | the html of every verse | BHSA |
| `data/words.parquet` | the html of every word | BHSA |
| `data/definitions.json` | verb definitions | [openscriptures/strongs](https://github.com/openscriptures/strongs) |

The first run downloads the BHSA corpus (about 270 MB) into `~/text-fabric-data` through
[Text-Fabric](https://github.com/annotation/text-fabric), and needs network access. Later runs reuse
that download and take under a minute.

To rebuild from scratch, delete the files above and run the command again.

## 2. Start the app

```bash
uv run main.py
```

The app is served on http://localhost:7777. Use `uv run main.py debug` for hot reloading.

## Docker

The image builds the data itself, so building it needs network access:

```bash
docker build -t hegram .
docker run -p 7777:7777 hegram
```
