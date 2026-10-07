from hegram.books import book_dropdown_data

COMMON_BINYANIM = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]

# Bar chart series, one per tense, for the binyan/tense charts.
TENSE_SERIES = [
    {"name": "Qatal", "color": "red.6"},
    {"name": "Yiqtol", "color": "green.6"},
    {"name": "Wayyiqtol", "color": "indigo.6"},
    {"name": "Imperative", "color": "grape.6"},
    {"name": "Infinitive (abslute)", "color": "teal.6"},
    {"name": "Infinitive (construct)", "color": "yellow.6"},
    {"name": "Participle", "color": "pink.6"},
    {"name": "Participle (passive)", "color": "lime.6"},
]

dropdown_data = {
    "Book": book_dropdown_data,
    "Binyan": [
        {"group": "Communs", "items": COMMON_BINYANIM},
        {
            "group": "Rares",
            "items": [
                "Hishtafal",
                "Passiveqal",
                "Hotpaal",
                "Nitpael",
                "Poal",
                "Poel",
                "Hitpoel",
                "Peal",
                "Tifal",
                "Etpaal",
                "Pael",
                "Hafel",
                "Hitpeel",
                "Hitpaal",
                "Peil",
                "Etpeel",
                "Afel",
                "Shafel",
            ],
        },
    ],
    "Tense": [
        {"value": "Qatal", "label": "Accompli"},
        {"value": "Yiqtol", "label": "Inaccompli"},
        {"value": "Wayyiqtol", "label": "Inaccompli Inversif"},
        {"value": "Imperative", "label": "Impératif"},
        {"value": "Participle", "label": "Participe actif"},
        {"value": "Participle (passive)", "label": "Participe passif"},
        {"value": "Infinitive (construct)", "label": "Infinitif construit"},
        {"value": "Infinitive (abslute)", "label": "Infinitif absolu"},
    ],
    "Person": [
        {"value": "1", "label": "1ère"},
        {"value": "2", "label": "2ème"},
        {"value": "3", "label": "3ème"},
    ],
    "Gender": [
        {"value": "M", "label": "Masculin"},
        {"value": "F", "label": "Féminin"},
    ],
    "Number": [
        {"value": "Singular", "label": "Singulier"},
        {"value": "Plural", "label": "Pluriel"},
    ],
}

answer_data = [
    {"label": "1S", "value": "1S"},
    {"label": "2MS", "value": "2MS"},
    {"label": "2FS", "value": "2FS"},
    {"label": "3MS", "value": "3MS"},
    {"label": "3FS", "value": "3FS"},
    {"label": "1P", "value": "1P"},
    {"label": "2MP", "value": "2MP"},
    {"label": "2FP", "value": "2FP"},
    {"label": "3P", "value": "3P"},
    {"label": "3MP", "value": "3MP"},
    {"label": "3FP", "value": "3FP"},
    {"label": "MS", "value": "MS"},
    {"label": "FS", "value": "FS"},
    {"label": "MP", "value": "MP"},
    {"label": "FP", "value": "FP"},
    {"label": "", "value": ""},
]

en_to_fr = {
    "Tense": {
        "Qatal": "Accompli",
        "Yiqtol": "Inaccompli",
        "Wayyiqtol": "Inaccompli Inversif",
        "Imperative": "Impératif",
        "Participle": "Participe actif",
        "Participle (passive)": "Participe passif",
        "Infinitive (construct)": "Infinitif construit",
        "Infinitive (abslute)": "Infinitif absolu",
    },
    "Person": {
        "1": "1ère",
        "2": "2ème",
        "3": "3ème",
    },
    "Gender": {"F": "Féminin", "M": "Masculin"},
    "Number": {
        "Plural": "Pluriel",
        "Singular": "Singulier",
    },
}
