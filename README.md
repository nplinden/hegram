A webapp for analysing binyanim and tenses occurrence in the Hebrew Bible.

This mostly exists as a personal learning project for Plotly's dash.

# Running Hegram

You need [uv](https://github.com/astral-sh/uv) to run Hegram.

## 1. Build the data

The corpus data is not versioned and must be generated once after cloning:

```bash
git clone https://github.com/nplinden/hegram.git
cd hegram
uv run --group build python -m hegram.build_dataframes
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

The app is served on http://localhost:5844. Use `uv run main.py debug` for hot reloading.

## Docker

Every push to `main` publishes an image to `ghcr.io/nplinden/hegram`. The sample [compose.yaml](compose.yaml)
runs it on http://localhost:5844:

```bash
docker compose up -d            # pull the published image and start it
docker compose up -d --build    # or build it from this repository
```

To build and run the image without Compose:

```bash
docker build -t hegram .
docker run -p 5844:5844 hegram
```

The image builds the data itself, so building it needs network access.
