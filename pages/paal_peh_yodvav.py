import dash
from pages.conj_layout import make_page

dash.register_page(__name__, path="/paal_peh_yodvav")

layout = make_page(
    page_id="paal-peh-yodvav",
    title="Paal — Verbe פ״יו",
    root="ילד",
    asset="assets/paal_peh_yodvav.svg",
    absolu="יָלֹד",
    construit="לָלֶדֶת",
    accompli=[
        ("1S",  "יָלַדְתִּי"), ("2MS", "יָלַדְתָּ"),  ("2FS", "יָלַדְתְּ"),
        ("3MS", "יָלַד"),      ("3FS", "יָֽלְדָה"),   ("1P",  "יָלַדְנוּ"),
        ("2MP", "יְלַדְתֶּם"), ("2FP", "יְלַדְתֶּן"), ("3M",  "יָֽלְדוּ"),
    ],
    inaccompli=[
        ("1S",  "אֵלֵד"),    ("2MS", "תֵּלֵד"),    ("2FS", "תֵּלְדִי"),
        ("3MS", "יֵלֵד"),    ("3FS", "תֵּלֵד"),    ("1P",  "נֵלֵד"),
        ("2MP", "תֵּלְדוּ"), ("2FP", "תֵּלֵדְנָה, תֵּלַדְנָה"), ("3MP", "יֵלְדוּ"),
        ("3FP", "תֵּלֵדְנָה, תֵּלַדְנָה"),
    ],
    imperatif=[
        ("2MS", "לֵד"), ("2FS", "לְדִי"), ("2MP", "לְדוּ"), ("2FP", "לֵדְנָה"),
    ],
    participe=[
        ("MS", "יוֹלֵד"), ("FS", "יוֹלֶדֶת"), ("MP", "יוֹלְדִים"), ("FP", "יוֹלְדוֹת"),
    ],
)
