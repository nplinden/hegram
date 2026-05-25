import dash
from pages.conj_layout import make_page

dash.register_page(__name__, path="/paal_peh_nun")

layout = make_page(
    page_id="paal-peh-nun",
    title="Paal — Verbe פ״נ",
    root="נפל",
    asset="assets/paal_peh_nun.svg",
    absolu="נָפוֹל",
    construit="לִנְפֹּל",
    accompli=[
        ("1S",  "נָפַ֫לְתִּי"), ("2MS", "נָפַ֫לְתָּ"),  ("2FS", "נָפַלְתְּ"),
        ("3MS", "נָפַל"),       ("3FS", "נָֽפְלָה"),    ("1P",  "נָפַ֫לְנוּ"),
        ("2MP", "נְפַלְתֶּם"),  ("2FP", "נְפַלְתֶּן"),  ("3M",  "נָֽפְלוּ"),
    ],
    inaccompli=[
        ("1S",  "אֶפֹּל"),   ("2MS", "תִּפֹּל"),   ("2FS", "תִּפְּלִי"),
        ("3MS", "יִפֹּל"),   ("3FS", "תִּפֹּל"),   ("1P",  "נִפֹּל"),
        ("2MP", "תִּפְּלוּ"), ("2FP", "תִּפֹּלְנָה"), ("3MP", "יִפְּלוּ"),
        ("3FP", "תִּפֹּלְנָה"),
    ],
    imperatif=[
        ("2MS", "נְפֹל"), ("2FS", "נִפְלִי"), ("2MP", "נִפְלוּ"), ("2FP", "נְפֹלְנָה"),
    ],
    participe=[
        ("MS", "נוֹפֵל"), ("FS", "נוֹפֶלֶת"), ("MP", "נוֹפְלִים"), ("FP", "נוֹפְלוֹת"),
    ],
)
