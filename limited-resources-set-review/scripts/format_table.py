#!/usr/bin/env python3
"""Converte o JSON de notas em uma tabela separada por tab, agrupada por cor.

uso: format_table.py <notas.json> <cards.txt> <saida.txt> [--tab-width N]

As colunas são separadas por tabs, com quantos tabs forem necessários para
alinhar num editor com tabulação de N colunas (padrão 4).

notas.json: [{"card": str, "lsv": str, "marshall": str, "uncertain": bool}]
  Subnotas já devem vir no texto da nota, ex.: "C+ (BA: B-)".
cards.txt: saída de fetch_set.py (nome | raridade | custo | cores | tipo).
"""
import json
import sys

GROUPS = ["Branco", "Azul", "Preto", "Vermelho", "Verde", "Multicolor", "Incolor", "Terrenos"]
MONO = {"W": "Branco", "U": "Azul", "B": "Preto", "R": "Vermelho", "G": "Verde"}
UNKNOWN = "Sem cor identificada"


def load_cards(path):
    cards = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) < 5:
                continue
            name, colors, type_line = parts[0], parts[3], parts[4]
            cards[name.lower()] = (colors, type_line)
            cards.setdefault(name.split(" // ")[0].lower(), (colors, type_line))
    return cards


def group_of(name, cards):
    info = cards.get(name.lower()) or cards.get(name.split(" // ")[0].lower())
    if not info:
        return UNKNOWN
    colors, type_line = info
    if "Land" in type_line.split(" // ")[0]:
        return "Terrenos"
    colors = colors.replace("C", "")
    if len(colors) == 1:
        return MONO[colors]
    return "Multicolor" if colors else "Incolor"


def pad(text, width, tab):
    """Texto seguido dos tabs necessários para chegar à coluna `width`."""
    return text + "\t" * (width // tab - len(text) // tab)


def main(src, cards_path, dst, tab=4):
    with open(src, encoding="utf-8") as f:
        rows = json.load(f)
    cards = load_cards(cards_path)

    grouped = {}
    for r in rows:
        name = r["card"].split(" // ")[0] + (" (?)" if r.get("uncertain") else "")
        grouped.setdefault(group_of(r["card"], cards), []).append(
            (name, r.get("lsv") or "-", r.get("marshall") or "-")
        )

    all_rows = [("Carta", "LSV", "Marshall")] + [row for rs in grouped.values() for row in rs]
    w0, w1 = ((max(len(row[i]) for row in all_rows) // tab + 1) * tab for i in (0, 1))

    def fmt(row):
        return pad(row[0], w0, tab) + pad(row[1], w1, tab) + row[2]

    lines = []
    for g in GROUPS + [UNKNOWN]:
        if g not in grouped:
            continue
        if lines:
            lines.append("")
        lines += [g, fmt(all_rows[0])]
        lines += [fmt(row) for row in sorted(grouped[g], key=lambda t: t[0].lower())]

    if any(r.get("uncertain") for r in rows):
        lines += ["", "(?) = nome ou nota incerta, conferir no vídeo"]
    lines.append("SB = sideboard, BA = build-around")
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(rows)} cartas escritas em {dst}")
    if UNKNOWN in grouped:
        print(f"aviso: {len(grouped[UNKNOWN])} cartas sem cor identificada: "
              + ", ".join(t[0] for t in grouped[UNKNOWN]))


if __name__ == "__main__":
    args = sys.argv[1:]
    tab = 4
    if "--tab-width" in args:
        i = args.index("--tab-width")
        tab = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 3:
        sys.exit("uso: format_table.py <notas.json> <cards.txt> <saida.txt> [--tab-width N]")
    main(*args, tab=tab)
