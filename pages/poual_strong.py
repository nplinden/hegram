import dash
from pages.conj_layout import make_page

dash.register_page(__name__, path="/poual_strong")

layout = make_page(
    page_id="poual-strong",
    title="Poual — Verbe fort",
    root="ילד",
    asset="assets/poual_strong.svg",
    accompli=[
        ("1S",  "יֻלַּדְתִּי"), ("2MS", "יֻלַּדְתָּ"),  ("2FS", "יֻלַּדְתְּ"),
        ("3MS", "יֻלַּדְ"),     ("3FS", "יֻלְּדָה"),   ("1P",  "יֻלַּדְנוּ"),
        ("2MP", "יֻלַּדְתֶּם"), ("2FP", "יֻלַּדְתֶּן"), ("3MP", "יֻלְּדוּ"),
        ("3FP", "יֻלְּדוּ"),
    ],
    inaccompli=[
        ("1S",  "אֲיֻלַּד"),   ("2MS", "תְּיֻלַּד"),   ("2FS", "תְּיֻלְּדִי"),
        ("3MS", "יְיֻלַּד"),   ("3FS", "תְּיֻלַּד"),   ("1P",  "נְיֻלַּד"),
        ("2MP", "תְּיֻלְּדוּ"), ("2FP", "תְּיֻלַּדְנָה"), ("3MP", "יְיֻלְּדוּ"),
        ("3FP", "תְּיֻלַּדְנָה"),
    ],
    participe=[
        ("MS", "מְיֻלַּד"), ("FS", "מְיֻלֶּדֶת"), ("MP", "מְיֻלָּדִים"), ("FP", "מְיֻלָּדוֹת"),
    ],
)
