"""Pilot rules. Rule hits are candidates, never validated pressure articles.

Synthetic examples in tests contain no vendor text. Frozen with the manifest.
"""
from __future__ import annotations

import html
from dataclasses import dataclass

import regex

L, R, W = r"(?<!\p{L})", r"(?!\p{L})", r"\p{L}*"
FLAGS = regex.I | regex.V1


def rx(pattern):
    return regex.compile(pattern, FLAGS)


PLACE_PATTERNS = {
    "Funtana": L + r"funtan\p{L}*",
    "Vrsar": L + r"vrsar\p{L}*",
    "Tar-Vabriga": L + r"(?:vabrig\p{L}*|tar[- ]vabrig\p{L}*|(?:u|iz|općin\p{L}*) tar(?:u|a)?)" + R,
    "Lopar": L + r"lopar\p{L}*",
    "Baška": L + r"ba[šs]k(?:a|e|oj|u|om)" + R + r"(?!\s+vod\p{L}*)",
    "Novalja": L + r"(?:novalj\p{L}*|zr[ćc](?:e|a|u))" + R,
    "Povljana": L + r"povljan\p{L}*",
    "Brtonigla": L + r"brtonigl\p{L}*",
    "Tučepi": L + r"tu[čc]ep\p{L}*",
    "Nin": L + r"(?:(?:u|iz|grad\p{L}*) nin(?:u|a|om)?|ninsk\p{L}* lagun\p{L}*|kraljičin\p{L}* plaž\p{L}*)" + R,
    "Brela": L + r"brel(?:a|ima|u|e|sk\p{L}*)" + R,
    "Medulin": L + r"(?:medulin\p{L}*|premantur\p{L}*|banjol\p{L}*|kamenjak\p{L}*)",
    "Podgora": L + r"podgor(?:a|e|i|u|om|sk\p{L}*)" + R,
    "Split": L + r"(?:split(?:a|u|om)?|splitsk\p{L}*|spli[ćc]an\p{L}*)" + R,
    "Dubrovnik": L + r"(?:dubrovnik\p{L}*|dubrova[čc]k\p{L}*|dubrov[čc]an\p{L}*|stradun\p{L}*)",
    "Rovinj": L + r"rovinj\p{L}*",
    "Poreč": L + r"(?:pore[čc](?:a|u|om)?|pore[čc]k\p{L}*|pore[čc]an\p{L}*)" + R,
    "Umag": L + r"(?:umag\p{L}*|uma[šs]k\p{L}*)",
    "Hvar": L + r"(?:(?:u|iz) hvar(?:u|a)|grad\p{L}* hvar\p{L}*)" + R,
    "Makarska": L + r"(?:makarsk\p{L}*|makran\p{L}*)",
    "Baška Voda": L + r"ba[šs]k\p{L}* vod\p{L}*",
    "Zadar": L + r"(?:zad(?:ar|ra|ru|rom)|zadarsk\p{L}*|zadran\p{L}*)" + R,
    "Pula": L + r"(?:pul(?:a|e|i|u|om)|pulsk\p{L}*|pulj(?:an|ank)\p{L}*)" + R,
}
PLACES = {k: rx(v) for k, v in PLACE_PATTERNS.items()}
SQL_TOURISM = r"turis|turiz|no[ćc]enj|apartman|iznajmlj|pla[žz]|gost|sezon|hotel|kamp|kruzer|posjetitelj|smje[šs]taj|booking|airbnb"
TOURISM_STRONG = rx(r"turis|turiz|no[ćc]enj|apartman|iznajmlj|pla[žz]|hotel|kamp|kruzer|smje[šs]taj|booking|airbnb")
TOURISM = rx(SQL_TOURISM)
SPORT = rx(r"nogomet|utakmic|ko[šs]ark|rukomet|vaterpol|derbi|trener|igra[čc]|navija[čc]|gostovanj|tenis|hajduk|dinamo")
TRAFFIC = rx(r"promet|kolon|autocest|semafor|parkir|nesre[ćc]|sudar|voza[čc]|zastoj|trajekt|katamaran|aerodrom|zra[čc]n\p{L}* luk|granic|naplat")
COMPLAINT = rx(r"mještan|stanovnik|buka|smeć|voda|gradnja|apartman|gužv|parking|nezadovolj|žal\p{L}*")
FAMILY_PATTERNS = {
    "F1": r"overtour|over-tour|prekomjern\p{L}* turiz|masovn\p{L}* turiz|pretjeran\p{L}* turiz|previ[šs]e (?:turist|gost)",
    "F2": r"turistifik|disneyfik|diznifik",
    "F3": r"gu[žz]v|prenapu[čc]|pretrpan|prepun\p{L}* turist|krcat\p{L}* (?:turist|pla[žz])",
    "F4": r"apartmaniz|kratkoro[čc]n\p{L}* (?:najam|najm)|iselj\p{L}*.{0,50}(?:jezgr|centr)|(?:jezgr|centr)\p{L}*.{0,50}iselj",
    "F5": r"pijan\p{L}* turist|turist\p{L}*.{0,30}(?:pijan|polugol|urinir|povra[ćc]|buk)|buk\p{L}*.{0,30}turist|(?:buk|zvuk|kota[čc])\p{L}* kofer",
    "F6": r"(?:ograni[čc]|kvot|zabran)\p{L}*.{0,40}(?:kruzer|izletnik|posjetitelj)|(?:kruzer|izletnik)\p{L}*.{0,40}(?:ograni[čc]|kvot|zabran)",
    "F7": r"(?:prosvjed|peticij|pobun)\p{L}*.{0,55}(?:turis|apartman)|(?:turis|apartman)\p{L}*.{0,55}(?:prosvjed|peticij|pobun)",
    "G": r"nosiv\p{L}* kapacitet|prihvatn\p{L}* kapacitet|plan\p{L}* upravljanja destinacij",
    "S": r"betoniz|preizgrađen|preizgradjen",
}
FAMILIES = {k: rx(v) for k, v in FAMILY_PATTERNS.items()}
NEGATED_CROWD = rx(r"bez\s+gu[žz]v|nema\s+gu[žz]v|izbjeg\p{L}*\s+gu[žz]v")
STRIPS = rx(r"splitsko[- ]dalmatinsk\p{L}*|dubrova[čc]ko[- ]neretvansk\p{L}*|zadarsk\p{L}* županij\p{L}*|makarsk\p{L}* rivijer\p{L}*|grgur\p{L}* ninsk\p{L}*|ba[šs]k\p{L}* vod\p{L}*|hajduk\p{L}* split\p{L}*|rnk split\p{L}*|banana split")
TAGLINE = rx(r"\s*(?:[-|–]\s*)?novosti iz pore[čc]a i okolice[^\n]*")
HTML_TAG = rx(r"<[^>]+>")


@dataclass(frozen=True)
class ContextRule:
    name: str
    description: str


CONTEXT_RULES = [
    ContextRule("sport", "Weak tourism words in a sport window do not establish tourism"),
    ContextRule("traffic", "F3 crowding plus transport is T, not pressure; other families survive"),
    ContextRule("negation", "Without crowds is not a positive F3 candidate"),
    ContextRule("Hvar", "Only explicit town constructions; island mentions excluded"),
    ContextRule("Nin", "Location or lagoon constructions; newspaper and personal name excluded"),
    ContextRule("Baška", "Remove Baška Voda before matching Baška"),
]


def clean(text):
    text = html.unescape(HTML_TAG.sub(" ", text or ""))
    return regex.sub(r"[\t\r ]+", " ", TAGLINE.sub(" ", text)).strip()


def place_text(text, place):
    if place == "Baška Voda":
        return text
    return STRIPS.sub(lambda m: " " * len(m.group()), text)


def flags(window):
    tourism = bool(TOURISM.search(window))
    sport_veto = bool(SPORT.search(window)) and not TOURISM_STRONG.search(window)
    if not tourism or sport_veto:
        return False, [], bool(TRAFFIC.search(window)), sport_veto
    fam = [k for k, v in FAMILIES.items() if v.search(window)]
    traffic = bool(TRAFFIC.search(window))
    if "F3" in fam and (traffic or NEGATED_CROWD.search(window)):
        fam.remove("F3")
    return True, fam, traffic, sport_veto


def windows(text, place):
    """At most neighbouring sentences and 300 characters, centred on a place.

    Contexts preserve +/-500 characters locally for the later width checks.
    """
    target = place_text(text, place)
    sentences = list(regex.finditer(r"[^.!?\n]+[.!?]?", target))
    if not sentences:
        return
    ends = [s.end() for s in sentences]
    import bisect
    seen = set()
    for match in PLACES[place].finditer(target):
        j = min(bisect.bisect_right(ends, match.start()), len(sentences)-1)
        start = sentences[max(0, j-1)].start()
        end = sentences[min(len(sentences)-1, j+1)].end()
        center = (match.start()+match.end())//2
        start, end = max(start, center-150), min(end, center+150)
        window = target[start:end].strip()
        if not window or window in seen:
            continue
        seen.add(window)
        tourism, fam, traffic, sport = flags(window)
        if tourism:
            masked = PLACES[place].sub("[MJESTO]", window)
            yield dict(window=window, masked_window=masked,
                       context=text[max(0,match.start()-500):min(len(text),match.end()+500)],
                       families="|".join(fam), candidate=any(x.startswith("F") for x in fam),
                       traffic=traffic, recall_score=len(COMPLAINT.findall(window)))
