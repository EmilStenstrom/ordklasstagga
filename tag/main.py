# -*- coding: utf-8 -*-
from bottle import route, request, view
import requests
import re

JSON_TAGGER_ADDRESS = "http://json-tagger.herokuapp.com/tag"
DEFAULT_SENTENCE = "Fördomen har alltid sin rot i vardagslivet - Olof Palme"
POS_MAPPING = {
    "ADJ": "Adjektiv",
    "ADP": "Adposition",
    "ADV": "Adverb",
    "AUX": "Hjälpverb",
    "CCONJ": "Samordnade konjunktion",
    "DET": "Determinativa pronomen",
    "INTJ": "Interjektion",
    "NOUN": "Substantiv",
    "NUM": "Räkneord",
    "PART": "Partikel",
    "PRON": "Pronomen",
    "PROPN": "Egennamn",
    "PUNCT": "Skiljetecken",
    "SCONJ": "Subjunktion",
    "SYM": "Symbol",
    "VERB": "Verb",
}

# Specific to Swedish (http://universaldependencies.org/sv/feat/index.html)
FEATURES = {
    "Abbr=Yes": {"group": "Förkortning", "name": "Förkortning"},
    "Case=Nom": {"group": "Kasus", "name": "Nominativ"},
    "Case=Acc": {"group": "Kasus", "name": "Ackusativ"},
    "Case=Gen": {"group": "Kasus", "name": "Genetiv"},
    "Definite=Ind": {"group": "Species", "name": "Obestämd"},
    "Definite=Def": {"group": "Species", "name": "Bestämd"},
    "Degree=Pos": {"group": "Komparation", "name": "Positiv"},
    "Degree=Cmp": {"group": "Komparation", "name": "Komparativ"},
    "Degree=Sup": {"group": "Komparation", "name": "Superlativ"},
    "Foreign=Yes": {"group": "Utländskt ord", "name": "Utländskt ord"},
    "Gender=Com": {"group": "Genus", "name": "Utrum"},
    "Gender=Neut": {"group": "Genus", "name": "Neutrum"},
    "Gender=Masc": {"group": "Genus", "name": "Maskulinum"},
    "Mood=Ind": {"group": "Modus", "name": "Indikativ"},
    "Mood=Imp": {"group": "Modus", "name": "Imperativ"},
    "Mood=Sub": {"group": "Modus", "name": "Konjunktiv"},
    "NumType=Card": {"group": "Nummer", "name": "Nummer"},
    "Number=Sing": {"group": "Numerus", "name": "Singular"},
    "Number=Plur": {"group": "Numerus", "name": "Plural"},
    "Polarity=Neg": {"group": "Polaritet", "name": "Negativ"},
    "Poss=Yes": {"group": "Possessiv", "name": "Possessiv"},
    "PronType=Prs": {"group": "Pronomentyp", "name": "Personligt"},
    "PronType=Art": {"group": "Pronomentyp", "name": "Artikel"},
    "PronType=Int": {"group": "Pronomentyp", "name": "Interrogativ"},
    "PronType=Rel": {"group": "Pronomentyp", "name": "Relationell"},
    "PronType=Tot": {"group": "Pronomentyp", "name": "Kvantitativ"},
    "PronType=Ind": {"group": "Pronomentyp", "name": "Indefinit"},
    "PronType=Dem": {"group": "Pronomentyp", "name": "Demonstrativ"},
    "PronType=Rcp": {"group": "Pronomentyp", "name": "Reciprokt"},
    "PronType=Neg": {"group": "Pronomentyp", "name": "Negativ"},
    "Tense=Pres": {"group": "Tempus", "name": "Presens"},
    "Tense=Past": {"group": "Tempus", "name": "Preteritum"},
    "VerbForm=Inf": {"group": "Verbform", "name": "Infinitiv"},
    "VerbForm=Fin": {"group": "Verbform", "name": "Finit"},
    "VerbForm=Part": {"group": "Verbform", "name": "Particip"},
    "VerbForm=Sup": {"group": "Verbform", "name": "Supinum"},
    "Voice=Act": {"group": "Diates", "name": "Aktivum"},
    "Voice=Pass": {"group": "Diates", "name": "Passivum"},
}

@route('/', method=["get", "post"])
@view('tag/views/index')
def index():
    data = request.POST.getunicode("data", "").encode("utf-8")

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
                if word["suc_tags"]["features"]:
                    features = re.split(r"\||\/", word["suc_tags"]["features"])
                    features = [MORPH_MAPPING[feat] for feat in features if feat != "-"]

                out_sentence.append({
                    "word_form": word["word_form"],
                    "lemma": word["lemma"],
                    "pos_tag": POS_MAPPING[word["suc_tags"]["pos_tag"]],
                    "morph_feat": features,
                })

            out_sentences.append(out_sentence)

        return {
            "data": data,
            "result": out_sentences,
        }

    return {
        "data": DEFAULT_SENTENCE,
    }
