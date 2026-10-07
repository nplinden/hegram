# Books of the Hebrew Bible, in canonical order: (BHSA name, French name, section, Mechon Mamre page pattern).
# The Mechon Mamre pattern takes the chapter code, see hegram.mechon_mamre.verse_to_url.
BOOKS = [
    ("Genesis", "La Genèse", "Torah", "ft01%s.htm"),
    ("Exodus", "L'Exode", "Torah", "ft02%s.htm"),
    ("Leviticus", "Le Lévitique", "Torah", "ft03%s.htm"),
    ("Numbers", "Les Nombres", "Torah", "ft04%s.htm"),
    ("Deuteronomy", "Le Deutéronome", "Torah", "ft05%s.htm"),
    ("Joshua", "Josué", "Nevi'im", "ft06%s.htm"),
    ("Judges", "Les Juges", "Nevi'im", "ft07%s.htm"),
    ("1_Samuel", "1 Samuel", "Nevi'im", "ft08a%s.htm"),
    ("2_Samuel", "2 Samuel", "Nevi'im", "ft08b%s.htm"),
    ("1_Kings", "1 Rois", "Nevi'im", "ft09a%s.htm"),
    ("2_Kings", "2 Rois", "Nevi'im", "ft09b%s.htm"),
    ("Isaiah", "Isaïe", "Nevi'im", "ft10%s.htm"),
    ("Jeremiah", "Jérémie", "Nevi'im", "ft11%s.htm"),
    ("Ezekiel", "Ézéchiel", "Nevi'im", "ft12%s.htm"),
    ("Hosea", "Osée", "Nevi'im", "ft13%s.htm"),
    ("Joel", "Joël", "Nevi'im", "ft14%s.htm"),
    ("Amos", "Amos", "Nevi'im", "ft15%s.htm"),
    ("Obadiah", "Obadia", "Nevi'im", "ft16%s.htm"),
    ("Jonah", "Jonas", "Nevi'im", "ft17%s.htm"),
    ("Micah", "Michée", "Nevi'im", "ft18%s.htm"),
    ("Nahum", "Nahoum", "Nevi'im", "ft19%s.htm"),
    ("Habakkuk", "Habacuc", "Nevi'im", "ft20%s.htm"),
    ("Zephaniah", "Cephania", "Nevi'im", "ft21%s.htm"),
    ("Haggai", "Haggaï", "Nevi'im", "ft22%s.htm"),
    ("Zechariah", "Zacharie", "Nevi'im", "ft23%s.htm"),
    ("Malachi", "Malachie", "Nevi'im", "ft24%s.htm"),
    ("Psalms", "Les Psaumes", "Ketouvim", "ft26%s.htm"),
    ("Job", "Job", "Ketouvim", "ft27%s.htm"),
    ("Proverbs", "Les Proverbes", "Ketouvim", "ft28%s.htm"),
    ("Ruth", "Ruth", "Ketouvim", "ft29%s.htm"),
    ("Song_of_songs", "Le Cantique des Cantiques", "Ketouvim", "ft30%s.htm"),
    ("Ecclesiastes", "L’Ecclésiaste", "Ketouvim", "ft31%s.htm"),
    ("Lamentations", "Les Lamentations", "Ketouvim", "ft32%s.htm"),
    ("Esther", "Esther", "Ketouvim", "ft33%s.htm"),
    ("Daniel", "Daniel", "Ketouvim", "ft34%s.htm"),
    ("Ezra", "Ezra", "Ketouvim", "ft35a%s.htm"),
    ("Nehemiah", "Néhémie", "Ketouvim", "ft35b%s.htm"),
    ("1_Chronicles", "1 Chroniques", "Ketouvim", "ft25a%s.htm"),
    ("2_Chronicles", "2 Chroniques", "Ketouvim", "ft25b%s.htm"),
]

en_to_fr_books = {en: fr for en, fr, _, _ in BOOKS}
fr_book_to_url = {fr: url for _, fr, _, url in BOOKS}

# Grouped options for the book MultiSelect, one group per section.
book_dropdown_data = [
    {"group": section, "items": [{"value": en, "label": fr} for en, fr, s, _ in BOOKS if s == section]}
    for section in dict.fromkeys(section for _, _, section, _ in BOOKS)
]
