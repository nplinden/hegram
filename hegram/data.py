binyanim_names = {
    "qal": "Paal",
    "piel": "Piel",
    "hif": "Hifil",
    "hit": "Hitpael",
    "hof": "Hofal",
    "pual": "Pual",
    "nif": "Nifal",
    "htpo": "hitpo“el",
    "poal": "po“al",
    "poel": "po“el",
    "afel": "af‘el",
    "etpa": "etpa“al",
    "etpe": "etpe‘el",
    "haf": "haf‘el",
    "hotp": "hotpa“al",
    "hsht": "hishtaf‘al",
    "htpa": "hitpa“al",
    "htpe": "hitpe‘el",
    "nit": "nitpa“el",
    "pael": "pa“el",
    "peal": "pe‘al",
    "peil": "pe‘il",
    "shaf": "shaf‘el",
    "tif": "tif‘al",
    "pasq": "passiveqal",
}
common_binyanim = ["Paal", "Piel", "Hifil", "Hitpael", "Hofal", "Pual", "Nifal"]
uncommon_binyanim = [v for v in binyanim_names.values() if v not in common_binyanim]
tense_names = {
    "perf": "Accompli",
    "impf": "Inaccompli",
    "wayq": "Wayyiqtol",
    "impv": "Impératif",
    "infa": "Infinitif Absolu",
    "infc": "Infinitif Construit",
    "ptca": "Participe Présent",
    "ptcp": "Participe Présent Passif",
}
