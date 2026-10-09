---
name: desmistificando-fii-to-audio
description: Gera o áudio de um Relatório Semanal de FIIs já extraído (.md do /desmistificando-fii-to-md) — uma faixa MP3 por seção e um .m4b com capítulos — para ouvir no celular pulando entre seções. Use quando o usuário pedir o áudio/leitura do relatório de fundos imobiliários.
argument-hint: <Relatorio FII NN - AAAA-MM-DD.md> [--voz ...] [--velocidade +10%] [--so 1,3] [--com-disclaimer]
---

# Áudio do relatório de FIIs

Script: `${CLAUDE_SKILL_DIR}/scripts/audio.py`. Ele usa `scripts/falar.py` para normalizar o texto para fala, `edge-tts` para gerar a voz e `ffmpeg`/`ffprobe` para tags e capítulos.

1. Se o usuário passou um HTML em vez do `.md`, rode antes o `/desmistificando-fii-to-md`.
2. Rode (leva alguns minutos):
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/audio.py "<relatorio.md>" [opções]
   ```
   Opções:
   - `--voz pt-BR-FranciscaNeural`: voz feminina (o padrão é `pt-BR-AntonioNeural`).
   - `--velocidade +10%`: deixa a leitura mais rápida.
   - `--so 1,3,5`: gera só essas seções (números do `.md`), útil para testes.
   - `--com-disclaimer`: inclui o disclaimer no áudio.
   - `--sem-m4b`: não gera o `.m4b`.
   - `--out pasta`: muda a pasta de saída.
   - `--force`: sobrescreve uma pasta que já existe. Pergunte ao usuário antes de usar.

   Se o `edge-tts` não estiver instalado, rode `uv tool install edge-tts`.
3. Abertura, Carteira Recomendada e Retornos não viram áudio (ficam só no `.md`); o Disclaimer só com `--com-disclaimer`.
4. Saída: pasta `<nome do md> - audio/`, com `NN - <título>.mp3` (um arquivo por seção), `Relatorio FII NN.m4b` (com capítulos) e `roteiro.txt` (o texto exatamente como foi falado).
5. Responda com o número de faixas, a duração total e o caminho da pasta.

A pronúncia é ajustada no `scripts/falar.py`: o dicionário `TICKERS` define como cada ticker é falado (ex.: `"TEPP": "tépi"`), os que não estão nele são soletrados por `LETRAS`, e `SIGLAS` cobre siglas e abreviações. Se o usuário reclamar de alguma pronúncia, ajuste ali e teste com `python3 ${CLAUDE_SKILL_DIR}/scripts/falar.py "frase"`.
