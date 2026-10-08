---
name: desmistificando-fii-to-md
description: Extrai o texto do Relatório Semanal de FIIs (DesmistificandoFII) a partir do HTML salvo pelo navegador, gerando um .md com uma seção por tópico/fundo, para guardar e analisar depois. Use quando o usuário passar o HTML do relatório semanal de fundos imobiliários.
argument-hint: <relatorio.html> [--out arquivo.md] [--force]
---

# Extrair o relatório de FIIs

Script: `${CLAUDE_SKILL_DIR}/scripts/extrair.py` (só Python padrão).

1. Se o usuário não passou o caminho, procure a pasta `relatorio-FIIS-*` mais recente em `~/Downloads` e confirme com ele.
2. Rode:
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/extrair.py "<relatorio.html>" [--out ...] [--force]
   ```
   A saída padrão é `Relatorio FII <edição> - <AAAA-MM-DD>.md`, na pasta do HTML. Se o arquivo já existir, pergunte antes de usar `--force`.
3. Responda em poucas linhas: o caminho do `.md` e a lista de seções que o script imprimiu. Repita qualquer `aviso:`, por exemplo um fundo abordado sem seção própria.

Se o script reclamar de "nenhum marcador 'Ouvir'" ou de "sem <main>", é porque o layout do site mudou ou o arquivo salvo não é a página do relatório. Nesse caso, investigue o HTML e ajuste o `extrair.py`: as seções são identificadas pelo texto `Ouvir`/`Order` que vem antes de cada tópico, e o título fica logo antes desse marcador, como cards `FII / TICKER / segmento / R$` ou um título de texto.

Para gerar o áudio depois: `/desmistificando-fii-to-audio <arquivo.md>`.
