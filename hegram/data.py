dropdown_data = {
    "Book": [
        {
            "group": "Torah",
            "items": [
                {"value": "Genesis", "label": "La Genèse"},
                {"value": "Exodus", "label": "L'Exode"},
                {"value": "Leviticus", "label": "Le Lévitique"},
                {"value": "Numbers", "label": "Les Nombres"},
                {"value": "Deuteronomy", "label": "Le Deutéronome"},
            ],
        },
        {
            "group": "Nevi'im",
            "items": [
                {"value": "Joshua", "label": "Josué"},
                {"value": "Judges", "label": "Les Juges"},
                {"value": "1_Samuel", "label": "1 Samuel"},
                {"value": "2_Samuel", "label": "2 Samuel"},
                {"value": "1_Kings", "label": "1 Rois"},
                {"value": "2_Kings", "label": "2 Rois"},
                {"value": "Isaiah", "label": "Isaïe"},
                {"value": "Jeremiah", "label": "Jérémie"},
                {"value": "Ezekiel", "label": "Ézéchiel"},
                {"value": "Hosea", "label": "Osée"},
                {"value": "Joel", "label": "Joël"},
                {"value": "Amos", "label": "Amos"},
                {"value": "Obadiah", "label": "Obadia"},
                {"value": "Jonah", "label": "Jonas"},
                {"value": "Micah", "label": "Michée"},
                {"value": "Nahum", "label": "Nahoum"},
                {"value": "Habakkuk", "label": "Habacuc"},
                {"value": "Zephaniah", "label": "Cephania"},
                {"value": "Haggai", "label": "Haggaï"},
                {"value": "Zechariah", "label": "Zacharie"},
                {"value": "Malachi", "label": "Malachie"},
            ],
        },
        {
            "group": "Ketouvim",
            "items": [
                {"value": "Psalms", "label": "Les Psaumes"},
                {"value": "Job", "label": "Job"},
                {"value": "Proverbs", "label": "Les Proverbes"},
                {"value": "Ruth", "label": "Ruth"},
                {"value": "Song_of_songs", "label": "Le Cantique des Cantiques"},
                {"value": "Ecclesiastes", "label": "L’Ecclésiaste"},
                {"value": "Lamentations", "label": "Les Lamentations"},
                {"value": "Esther", "label": "Esther"},
                {"value": "Daniel", "label": "Daniel"},
                {"value": "Ezra", "label": "Ezra"},
                {"value": "Nehemiah", "label": "Néhémie"},
                {"value": "1_Chronicles", "label": "1 Chroniques"},
                {"value": "2_Chronicles", "label": "2 Chroniques"},
            ],
        },
    ],
    "Binyan": [
        {"group": "Communs", "items": ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]},
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
