---
name: limited-resources-set-review
description: Extrai as notas que LSV (Luis Scott Vargas) e Marshall Sutcliffe dão para cada carta em transcripts de set review do podcast Limited Resources (Magic: the Gathering) e gera um .txt com a tabela Carta | LSV | Marshall (separada por tab, agrupada por cor), corrigindo os nomes das cartas pela lista oficial do Scryfall. Use quando o usuário fornecer transcripts de set review do Limited Resources.
argument-hint: <transcript.txt> [mais transcripts...] [--set CODIGO] [--out saida.txt]
---

# Notas do Limited Resources

Entrada: um ou mais transcripts (.txt) de vídeos de set review do Limited Resources, copiados do YouTube. Saída: um .txt com a nota de cada carta dada pelo LSV e pelo Marshall.

Os scripts ficam em `${CLAUDE_SKILL_DIR}/scripts/` (só Python padrão). Arquivos intermediários vão para o scratchpad.

## 1. Limpar os transcripts

O transcript do YouTube vem com uma linha de timestamp (`15:00`) e outra por extenso (`15 minutes`) antes de cada trecho. Para cada arquivo:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/clean_transcript.py "<transcript.txt>" > <scratchpad>/<nome>_clean.txt
```

A saída mantém os capítulos como `## Chapter N: <Cor>` e um marcador `[mm:ss]` por minuto. Leia a versão limpa inteira, em partes (um capítulo ou ~400 linhas por vez). Não pule trechos.

## 2. Identificar o set e baixar a lista oficial

- Use `--set` se o usuário passou. Senão, deduza pelo nome do arquivo ou pela abertura do episódio e confirme:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_set.py --find "<nome do set>"`
  Escolha o set principal (`expansion`/`core`/`draft_innovation`), não tokens/promos/commander. Se ficar ambíguo, pergunte ao usuário.
- Baixe as cartas: `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_set.py <code> > <scratchpad>/<code>_cards.txt` e leia o arquivo. Cada linha: `nome | raridade | custo | cores | tipo`.
- Cartas avaliadas que não estão no set (bonus sheet, "special guests", reimpressões): busque pelo nome e anexe ao mesmo arquivo, para que o script saiba a cor:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_set.py --named "Mind Twist" "Consider" >> <scratchpad>/<code>_cards.txt`

## 3. Extrair as notas, carta a carta

Sistema de notas do LR: letras de A a F com + e − (A+, A, A-, B+, ... F), mais duas subnotas: **Sideboard** e **Build-around** ("builder on B").

Para cada carta discutida:

- **Início da carta**: quando ela é apresentada ("next up is X", "X is a ..."), normalmente com o custo e o texto lidos em voz alta. Se houver capítulos (`## Chapter N: <Cor>`), eles indicam a cor. Alguns episódios, como os de raras, não têm capítulos.
- **Nota final**: a última nota que cada um dá para a carta. Ignore:
  - notas hipotéticas ("se matasse a criatura, seria A-");
  - notas de outras cartas citadas como comparação;
  - resumos especulativos de várias cartas ao mesmo tempo, a menos que fique claro que são as notas finais.
- **Normalizar**: "B minus" → `B-`, "B plus"/"B+" → `B+`, "a straight B" → `B`, "C C plus" (hesitação até chegar em C+) → `C+`. Se a pessoa der um intervalo e não escolher ("B+ A minus", "C plus B minus range") → `B+/A-`. Ninguém deu nota → `-`.
- **Subnotas**: anexe à nota: `C+ (BA: B-)` para build-around, `D (SB: C+)` para sideboard.
- **Concordância**: "I agree", "Yeah, same", "I'd say the same" = a mesma nota que o outro acabou de dar.

### Quem está falando

O transcript **não identifica quem fala**. Deduza pelos turnos da conversa:

- Marshall é o apresentador e abre o episódio ("My name is Marshall... joining me, Luis Scott Vargas").
- Alguém chamando "Luis" → quem fala é o Marshall. Alguém chamando "Marshall" → quem fala é o LSV.
- Perguntas como "What grade would you give it?" / "What do you think?" passam a vez para o outro.
- Respostas como "Yeah, I would give it...", "I'd go a little higher..." são do outro apresentador, não de quem acabou de dar a nota.
- Normalmente quem apresenta a carta dá a primeira nota e o outro responde, mas os dois se revezam ao longo do episódio. Acompanhe o fluxo da conversa.

Se as duas notas forem iguais, a atribuição não importa. Se forem diferentes e não der para saber qual é de quem, marque a carta como incerta.

## 4. Corrigir os nomes

As legendas automáticas erram muito os nomes ("constra" → "Constramp", "Fatal charm" → "Fate..."). Case cada carta com a lista oficial usando:

1. som parecido (pronúncia) e palavras em comum;
2. contexto: cor do capítulo, custo e tipo lidos em voz alta, raridade (o episódio diz se é de comuns/incomuns ou raras/míticas), texto descrito.

Use sempre o nome oficial do Scryfall. Para cartas de duas faces ou com feitiço preparado, guarde no JSON o nome completo (`Frente // Verso`): o script usa esse nome para achar a cor e exibe só a frente. Se não houver correspondência confiável, use o melhor palpite e marque como incerta.

## 5. Gerar o arquivo

Monte um JSON no scratchpad com todas as cartas de todos os transcripts (carta repetida em mais de um transcript: fica a última avaliação). A ordem não importa: o script agrupa e ordena.

```json
[
  {"card": "Nome Oficial", "lsv": "B", "marshall": "B-", "uncertain": false},
  {"card": "Outra Carta", "lsv": "C+ (BA: B-)", "marshall": "C+", "uncertain": true}
]
```

Depois rode:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/format_table.py <scratchpad>/notas.json <scratchpad>/<code>_cards.txt "<saida.txt>"
```

A saída é separada por tab e agrupada por cor, com a cor vinda do Scryfall: Branco, Azul, Preto, Vermelho, Verde, Multicolor (inclui híbridas), Incolor e Terrenos. Cada grupo fica em ordem alfabética. Se o script avisar que alguma carta ficou sem cor identificada, o nome no JSON não bate com o Scryfall: corrija e rode de novo.

Saída padrão: `<Nome do Set> - notas LR.txt` na pasta do primeiro transcript, ou o caminho de `--out`. Se o arquivo já existir, pergunte antes de sobrescrever.

## 6. Relatório no chat

Diga ao usuário, de forma curta:

- quantas cartas foram avaliadas e onde o arquivo foi salvo;
- as cartas marcadas com `(?)`, com o motivo (nome duvidoso ou nota sem dono certo);
- cartas do set na raridade coberta pelo episódio que não apareceram na tabela (pode ser uma carta pulada ou um nome que não foi reconhecido).
