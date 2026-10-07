from pathlib import Path

# Everything is located from the repository root rather than the working directory,
# so the app and the build work wherever they are launched from.
ROOT = Path(__file__).resolve().parent.parent

# Generated corpus data (see README) and the prepositions table.
DATA_DIR = ROOT / "data"
# French translation of the Bible, one file per book, with index.json mapping BHSA books to them.
BIBLE_FR_DIR = ROOT / "json"
# Files served by Dash at /assets: stylesheets, fonts, conjugation charts.
ASSETS_DIR = ROOT / "assets"
