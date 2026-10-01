#!/usr/bin/env python3
"""Limpa um transcript do YouTube: remove timestamps, mantém capítulos e um marcador por minuto."""
import re
import sys

TS = re.compile(r"^(\d+):(\d{2})(?::(\d{2}))?$")
SPOKEN_TS = re.compile(r"^\d+ (seconds?|minutes?|hours?)\b.*$")
NOISE = re.compile(r"^\[(music|applause)\]$", re.I)


def main(path):
    out, para, last_min = [], [], -1

    def flush():
        if para:
            out.append(" ".join(para))
            para.clear()

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or SPOKEN_TS.match(line) or NOISE.match(line):
                continue
            m = TS.match(line)
            if m:
                a, b, c = m.groups()
                minutes = int(a) * 60 + int(b) if c else int(a)
                if minutes != last_min:
                    last_min = minutes
                    para.append(f"[{line}]")
                continue
            if line.startswith("Chapter "):
                flush()
                out.append(f"\n## {line}\n")
                continue
            para.append(line)
            if len(para) > 40:
                flush()
    flush()
    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: clean_transcript.py <transcript.txt>")
    main(sys.argv[1])
