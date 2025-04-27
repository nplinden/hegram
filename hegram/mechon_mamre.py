import string

en_books = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "1_Samuel",
    "2_Samuel",
    "1_Kings",
    "2_Kings",
    "Isaiah",
    "Jeremiah",
    "Ezekiel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Psalms",
    "Job",
    "Proverbs",
    "Ruth",
    "Song_of_songs",
    "Ecclesiastes",
    "Lamentations",
    "Esther",
    "Daniel",
    "Ezra",
    "Nehemiah",
    "1_Chronicles",
    "2_Chronicles",
]

en_to_fr_books = {
    "Genesis": "La Genèse",
    "Exodus": "L'Exode",
    "Leviticus": "Le Lévitique",
    "Numbers": "Les Nombres",
    "Deuteronomy": "Le Deutéronome",
    "Joshua": "Josué",
    "Judges": "Les Juges",
    "1_Samuel": "1 Samuel",
    "2_Samuel": "2 Samuel",
    "1_Kings": "1 Rois",
    "2_Kings": "2 Rois",
    "Isaiah": "Isaïe",
    "Jeremiah": "Jérémie",
    "Ezekiel": "Ézéchiel",
    "Hosea": "Osée",
    "Joel": "Joël",
    "Amos": "Amos",
    "Obadiah": "Obadia",
    "Jonah": "Jonas",
    "Micah": "Michée",
    "Nahum": "Nahoum",
    "Habakkuk": "Habacuc",
    "Zephaniah": "Cephania",
    "Haggai": "Haggaï",
    "Zechariah": "Zacharie",
    "Malachi": "Malachie",
    "Psalms": "Les Psaumes",
    "Job": "Job",
    "Proverbs": "Les Proverbes",
    "Ruth": "Ruth",
    "Song_of_songs": "Le Cantique des Cantiques",
    "Ecclesiastes": "L’Ecclésiaste",
    "Lamentations": "Les Lamentations",
    "Esther": "Esther",
    "Daniel": "Daniel",
    "Ezra": "Ezra",
    "Nehemiah": "Néhémie",
    "1_Chronicles": "1 Chroniques",
    "2_Chronicles": "2 Chroniques",
}

MM_ROOT = "https://mechon-mamre.org/f/ft/"
fr_book_to_url = {
    "La Genèse": "ft01%s.htm",
    "L'Exode": "ft02%s.htm",
    "Le Lévitique": "ft03%s.htm",
    "Les Nombres": "ft04%s.htm",
    "Le Deutéronome": "ft05%s.htm",
    "Josué": "ft06%s.htm",
    "Les Juges": "ft07%s.htm",
    "1 Samuel": "ft08a%s.htm",
    "2 Samuel": "ft08b%s.htm",
    "1 Rois": "ft09a%s.htm",
    "2 Rois": "ft09b%s.htm",
    "Isaïe": "ft10%s.htm",
    "Jérémie": "ft11%s.htm",
    "Ézéchiel": "ft12%s.htm",
    "Osée": "ft13%s.htm",
    "Joël": "ft14%s.htm",
    "Amos": "ft15%s.htm",
    "Obadia": "ft16%s.htm",
    "Jonas": "ft17%s.htm",
    "Michée": "ft18%s.htm",
    "Nahoum": "ft19%s.htm",
    "Habacuc": "ft20%s.htm",
    "Cephania": "ft21%s.htm",
    "Haggaï": "ft22%s.htm",
    "Zacharie": "ft23%s.htm",
    "Malachie": "ft24%s.htm",
    "Les Psaumes": "ft26%s.htm",
    "Job": "ft27%s.htm",
    "Les Proverbes": "ft28%s.htm",
    "Ruth": "ft29%s.htm",
    "Le Cantique des Cantiques": "ft30%s.htm",
    "L’Ecclésiaste": "ft31%s.htm",
    "Les Lamentations": "ft32%s.htm",
    "Esther": "ft33%s.htm",
    "Daniel": "ft34%s.htm",
    "Ezra": "ft35a%s.htm",
    "Néhémie": "ft35b%s.htm",
    "1 Chroniques": "ft25a%s.htm",
    "2 Chroniques": "ft25b%s.htm",
}


def verse_to_url(book, chapter):
    """
    Generates a URL for accessing a specific chapter of a biblical book on the Mechon Mamre website.

    Args:
        book (str): The name of the book in French (e.g., "La Genèse", "L'Exode")
        chapter (int): The chapter number

    Returns:
        str: Complete URL to access the chapter

    Example:
        >>> verse_to_url("La Genèse", 1)
        'https://mechon-mamre.org/f/ft/ft0101.htm'
        >>> verse_to_url("Les Psaumes", 119)
        'https://mechon-mamre.org/f/ft/ft26a9.htm'

    Note:
        For chapters >= 100, the URL uses a letter-number combination where:
        - The tens digit (minus 10) is converted to a letter (a-z)
        - The units digit remains as is
    """
    if chapter < 100:
        return MM_ROOT + fr_book_to_url[book] % f"{chapter:02d}"
    else:
        unit = chapter % 10
        tens = (chapter // 10) - 10
        return MM_ROOT + fr_book_to_url[book] % f"{string.ascii_letters[tens]}{unit}"
