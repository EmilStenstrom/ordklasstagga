# -*- coding: utf-8 -*-
from bottle import route, request, view
import requests
import re

JSON_TAGGER_ADDRESS = "http://json-tagger.herokuapp.com/tag"
DEFAULT_SENTENCE = "Fördomen har alltid sin rot i vardagslivet - Olof Palme"
POS_MAPPING = {
    "AB": "Adverb",
    "DT": "Determinerare",
    "HA": "Frågande/relativt adverb",
    "HD": "Frågande/relativ determinerare",
    "HP": "Frågande/relativt pronomen",
    "HS": "Frågande/relativt possessivt pronomen",
    "IE": "Infinitivmärke",
    "IN": "Interjektion",
    "JJ": "Adjektiv",
    "KN": "Konjunktion",
    "NN": "Substantiv",
    "PC": "Particip",
    "PL": "Partikel",
    "PM": "Egennamn",
    "PN": "Pronomen",
    "PP": "Preposition",
    "PS": "Possessivt pronomen",
    "RG": "Grundtal",
    "RO": "Ordningstal",
    "SN": "Subjunktion",
    "UO": "Utländskt ord",
    "VB": "Verb",
    "MAD": "Meningsavslutare",
    "MID": "Meningsdelare",
    "PAD": "Parvis skiljetecken",
}
MORPH_MAPPING = {
    "UTR": {"group": "Genus", "name": "Utrum"},
    "NEU": {"group": "Genus", "name": "Neutrum"},
    "MAS": {"group": "Genus", "name": "Maskulinum"},
    "SIN": {"group": "Numerus", "name": "Singular"},
    "PLU": {"group": "Numerus", "name": "Plural"},
    "IND": {"group": "Species", "name": "Obestämd"},
    "DEF": {"group": "Species", "name": "Bestämd"},
    "NOM": {"group": "Kasus", "name": "Nominativ"},
    "GEN": {"group": "Kasus", "name": "Genitiv"},
    "PRS": {"group": "Tempus", "name": "Presens"},
    "PRT": {"group": "Tempus", "name": "Imperfekt/Preteritum"},
    "SUP": {"group": "Tempus", "name": "Supinum"},
    "INF": {"group": "Tempus", "name": "Infinitiv"},
    "AKT": {"group": "Diates", "name": "Aktivum"},
    "SFO": {"group": "Diates", "name": "Passivum"},
    "KON": {"group": "Modus", "name": "Konjunktiv"},
    "IMP": {"group": "Modus", "name": "Imperativ"},
    "PRS": {"group": "Particip", "name": "Presens particip"},
    "PRF": {"group": "Particip", "name": "Perfekt particip"},
    "POS": {"group": "Komparation", "name": "Positiv"},
    "KOM": {"group": "Komparation", "name": "Komparativ"},
    "SUV": {"group": "Komparation", "name": "Superlativ"},
    "SUB": {"group": "Pronomenform", "name": "Subjekt"},
    "OBJ": {"group": "Pronomenform", "name": "Objekt"},
    "SMS": {"group": "Sammansatt", "name": "Sammansatt"},
    "AN": {"group": "Förkortning", "name": "Förkortning"},
}

@route('/', method=["get", "post"])
@view('tag/views/index')
def index():
    data = request.POST.getunicode("data", None)

    if request.POST:
        if not data:
            return {
                "error": "No data posted",
                "data": data,
            }

        response = requests.post(JSON_TAGGER_ADDRESS, data=data)
        result = response.json()

        sentences = result["sentences"]
        out_sentences = []
        for sentence in sentences:
            out_sentence = []
            for word in sentence:
                features = []
                if word["morph_feat"]:
                    features = re.split(r"\||\/", word["morph_feat"])
                    features = [MORPH_MAPPING[feat] for feat in features if feat != "-"]

                out_sentence.append({
                    "word_form": word["word_form"],
                    "pos_tag": POS_MAPPING[word["pos_tag"]],
                    "morph_feat": features,
                    "lemma": word["lemma"],
                })

            out_sentences.append(out_sentence)

        return {
            "data": data,
            "result": out_sentences,
        }

    return {
        "data": DEFAULT_SENTENCE,
    }
