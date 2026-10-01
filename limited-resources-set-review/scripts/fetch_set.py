#!/usr/bin/env python3
"""Consulta o Scryfall: encontra o código de um set ou lista as cartas dele.

uso:
  fetch_set.py --find "Reality Fracture"
  fetch_set.py fra
  fetch_set.py --named "Mind Twist" "Consider"   # cartas avulsas (ex.: bonus sheet)
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HEADERS = {"User-Agent": "limited-resources-set-review-skill/1.0", "Accept": "application/json"}


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def find(name):
    q = name.lower()
    for s in get("https://api.scryfall.com/sets")["data"]:
        if q in s["name"].lower():
            print(f"{s['code']}\t{s['name']}\t{s.get('released_at', '')}\t{s['set_type']}\t{s['card_count']}")


def line(c):
    face = c.get("card_faces", [{}])[0]
    cost = c.get("mana_cost") or face.get("mana_cost", "")
    colors = "".join(c.get("colors") or face.get("colors") or []) or "C"
    return f"{c['name']} | {c['rarity']} | {cost} | {colors} | {c.get('type_line', '')}"


def named(names):
    for n in names:
        url = "https://api.scryfall.com/cards/named?" + urllib.parse.urlencode({"fuzzy": n})
        try:
            print(line(get(url)))
        except urllib.error.HTTPError:
            print(f"não encontrada: {n}", file=sys.stderr)
        time.sleep(0.1)


def cards(code):
    url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode(
        {"q": f"e:{code}", "unique": "cards", "order": "set"}
    )
    while url:
        page = get(url)
        for c in page["data"]:
            print(line(c))
        url = page.get("next_page") if page.get("has_more") else None
        time.sleep(0.1)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--find":
        find(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "--named":
        named(sys.argv[2:])
    elif len(sys.argv) == 2:
        cards(sys.argv[1].lower())
    else:
        sys.exit(__doc__)
