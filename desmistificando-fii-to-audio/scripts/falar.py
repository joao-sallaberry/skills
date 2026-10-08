"""Normaliza texto do relatório para leitura em voz alta (pt-BR).

Números, valores em R$ e porcentagens simples ficam para o motor de voz, que já os lê bem.
Aqui tratamos o que ele costuma errar: tickers, siglas, datas, abreviações e símbolos.
"""
import re

# Siglas e abreviações → forma falada. Edite à vontade; a busca é por palavra inteira.
SIGLAS = {
    "FIIs": "fundos imobiliários",
    "FII": "fundo imobiliário",
    "FoFs": "fundos de fundos",
    "FoF": "fundo de fundos",
    "P/VP": "P sobre VP",
    "DY": "dividend yield",
    "IR": "imposto de renda",
    "PL": "patrimônio líquido",
    "IGPM": "IGP-M",
    "NTNB": "NTN-B",
    "IMAB5": "IMA-B 5",
    "IPCADP": "IPCA",
    "EUA": "Estados Unidos",
    "nº": "número",
}

LETRAS = {
    "A": "á", "B": "bê", "C": "cê", "D": "dê", "E": "é", "F": "éfe", "G": "gê", "H": "agá",
    "I": "i", "J": "jota", "K": "cá", "L": "éle", "M": "ême", "N": "ene", "O": "ó", "P": "pê",
    "Q": "quê", "R": "érre", "S": "ésse", "T": "tê", "U": "u", "V": "vê", "W": "dáblio",
    "X": "xis", "Y": "ípsilon", "Z": "zê",
}
NUMEROS_TICKER = {"3": "três", "4": "quatro", "5": "cinco", "6": "seis", "11": "onze", "12": "doze", "13": "treze"}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]

TICKER = re.compile(r"\b([A-Z]{4})(11|12|13|3|4|5|6)\b")
DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b")
URL = re.compile(r"https?://\S+")
VALOR_GRANDE = re.compile(r"R\$\s?([\d.,]+)\s?(MM|mi|milhões|milhão|bi|bilhões|bilhão|mil)\b")


def soletrar_ticker(m):
    letras = " ".join(LETRAS[c] for c in m.group(1))
    return f"{letras} {NUMEROS_TICKER[m.group(2)]}"


def data_falada(m):
    dia, mes, ano = int(m.group(1)), int(m.group(2)), m.group(3)
    if not (1 <= dia <= 31 and 1 <= mes <= 12):
        return m.group(0)
    s = f"{dia} de {MESES[mes - 1]}"
    return f"{s} de {ano}" if ano else s


def valor_grande(m):
    unidade = {"MM": "milhões", "mi": "milhões", "bi": "bilhões"}.get(m.group(2), m.group(2))
    if m.group(1) in ("1", "1,0") and unidade in ("milhões", "bilhões"):
        unidade = unidade.replace("ões", "ão")
    return f"{m.group(1)} {unidade} {'reais' if unidade == 'mil' else 'de reais'}"


def falar(texto):
    t = URL.sub("", texto)
    t = VALOR_GRANDE.sub(valor_grande, t)
    t = re.sub(r"\bMM\b", "milhões", t)
    t = DATA.sub(data_falada, t)
    for sigla, fala in sorted(SIGLAS.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"(?<![\w/]){re.escape(sigla)}(?![\w/])", fala, t)
    t = TICKER.sub(soletrar_ticker, t)
    t = re.sub(r"\bp\.p\.", "pontos percentuais", t)
    t = re.sub(r"%\s?a\.?a\.?(?=\W|$)", "% ao ano", t)
    t = re.sub(r"%\s?a\.?m\.?(?=\W|$)", "% ao mês", t)
    t = re.sub(r"/cota\b", " por cota", t)
    t = re.sub(r"/m²", " por metro quadrado", t)
    t = re.sub(r"\s*\+\s*", " mais ", t)
    t = re.sub(r"\s[xX]\s", " versus ", t)
    t = re.sub(r"[*_#|`]", "", t)
    t = t.replace("–", ",").replace("—", ",")
    return re.sub(r"[ \t]+", " ", t).strip()


if __name__ == "__main__":
    import sys
    for linha in sys.argv[1:] or sys.stdin:
        print(falar(linha.rstrip("\n")))
