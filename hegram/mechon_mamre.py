import string

from hegram.books import fr_book_to_url

MM_ROOT = "https://mechon-mamre.org/f/ft/"


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
