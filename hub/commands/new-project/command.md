---
# about
id: cmd-002
name: new-project
type: command
project: ""
description: Inicializa a estrutura .claude/ e as pastas de um novo projeto.
tags: [setup, project, init]

# history
author: ""
created: 2026-05-13
status: stable
version: 1.4.0
updated: 2026-05-15

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /new-project

Inicializa a estrutura `.claude/` e cria as pastas do projeto.

## Fluxo obrigatório — execute cada etapa em ordem, aguarde a resposta antes de avançar

**Etapa 1 — Pasta do projeto**

**[smart-suggestions: on]** Sugestão baseada no diretório atual da sessão.

Execute:

```bash
pwd
```

Use `AskUserQuestion` com 2 opções:
- **"Usar `<caminho retornado>`"** — confirma o diretório atual como pasta do projeto
- **"Informar outro caminho"** — solicita o caminho em texto livre

Se o usuário escolher "Informar outro caminho": pergunte em texto livre e aguarde a resposta.

Guarde o caminho escolhido como `<pasta>`.

**Etapa 2 — Nome do projeto**
Pergunte: "Qual o nome do projeto?"
Aguarde a resposta do usuário.

**Etapa 3 — Tipo de projeto**

Use `AskUserQuestion`:
- **"Branding"** — identidade visual e marca
- **"UX and UI"** — research, interfaces e design system
- **"Product Design"** — design estratégico de produto

Aguarde a resposta do usuário. Guarde como `<tipo>`.

**Etapa 3A — Sub-tipo (condicional)**

Se `<tipo>` for **Branding**: use `AskUserQuestion`:
- **"Plus"** — pacote essencial de marca
- **"Pro"** — pacote completo de marca
- **"Ultra"** — pacote abrangente de marca

Se `<tipo>` for **UX and UI**: use `AskUserQuestion` com `multiSelect: true`:
- **"UX Research"** — discovery e pesquisa com usuários
- **"Interface digital"** — app, web, site, loja, landing page
- **"Design System"** — biblioteca de componentes e tokens
- **"Outro (digitar)"** — escopo personalizado

Se `<tipo>` for **Product Design**: use `AskUserQuestion`:
- **"New product"** — produto sendo criado do zero
- **"Feature"** — nova funcionalidade em produto existente
- **"Redesign"** — revisão e melhoria de produto existente

Aguarde a resposta do usuário. Guarde como `<subtipo>`.

**Etapa 3B — Segmento de mercado**

Use `AskUserQuestion`:
- **"B2C"** — Business to Consumer
- **"B2B"** — Business to Business
- **"B2G"** — Business to Government
- **"C2C"** — Consumer to Consumer

Aguarde a resposta do usuário. Guarde como `<segmento>`.

**Etapa 3C — Macro categoria**

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/market_segments.json"
```

A partir do resultado, extraia as macro categorias do segmento `<segmento>`. Exiba em texto:

```
Macro categorias — <segmento>:

1. [nome] — [critério de agrupamento]
2. [nome] — [critério de agrupamento]
...

0. Voltar (escolher outro segmento)
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta.

Se o usuário escolher **0** ou **"Voltar"**: use `AskUserQuestion`:
- **"B2C"** — Business to Consumer
- **"B2B"** — Business to Business
- **"B2G"** — Business to Government
- **"C2C"** — Consumer to Consumer

Guarde a nova escolha como `<segmento>`. Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/market_segments.json"
```

Extraia as macro categorias do novo `<segmento>` e exiba a lista novamente:

```
Macro categorias — <segmento>:

1. [nome] — [critério de agrupamento]
2. [nome] — [critério de agrupamento]
...

0. Voltar (escolher outro segmento)
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta. Repita o tratamento de "Voltar" acima se necessário.

Guarde a escolha como `<macro>`.

**Etapa 3D — Categoria de mercado**

A partir do JSON já lido na Etapa 3C, extraia as categorias da macro `<macro>`. Exiba em texto:

```
Categorias — <macro>:

1. [categoria]
2. [categoria]
...

0. Voltar (escolher outro segmento)
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta.

Se o usuário escolher **0** ou **"Voltar"**: use `AskUserQuestion`:
- **"B2C"** — Business to Consumer
- **"B2B"** — Business to Business
- **"B2G"** — Business to Government
- **"C2C"** — Consumer to Consumer

Guarde a nova escolha como `<segmento>`. Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/market_segments.json"
```

Extraia as macro categorias do novo `<segmento>` e exiba:

```
Macro categorias — <segmento>:

1. [nome] — [critério de agrupamento]
2. [nome] — [critério de agrupamento]
...

0. Voltar (escolher outro segmento)
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta. Repita o tratamento de "Voltar" acima se necessário. Guarde como `<macro>`.

Extraia as categorias da nova `<macro>` e exiba:

```
Categorias — <macro>:

1. [categoria]
2. [categoria]
...

0. Voltar (escolher outro segmento)
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta. Repita o tratamento de "Voltar" acima se necessário.

Guarde a escolha como `<categoria>`.

**Etapa 4 — Público**

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/audience_segments.json"
```

A partir do resultado, extraia as dimensões do segmento `<segmento>`. Percorra cada dimensão em sequência, fazendo uma pergunta por dimensão.

**Primeira dimensão** — exiba em texto (sem opção Voltar) e aguarde resposta:

```
[nome da dimensão] — [descrição]:

1. [nome] — [referência]
2. [nome] — [referência]
3. [nome] — [referência]
4. [nome] — [referência]
```

**Demais dimensões** — exiba em texto e aguarde resposta:

```
[nome da dimensão] — [descrição]:

1. [nome] — [referência]
2. [nome] — [referência]
3. [nome] — [referência]
4. [nome] — [referência]

0. Voltar (recomeçar bloco público)
```

Se o usuário escolher **0** ou **"Voltar"** em qualquer dimensão: descarte todas as respostas do bloco público. A partir do JSON já lido, exiba novamente a primeira dimensão do segmento `<segmento>` (sem opção Voltar) e aguarde resposta. Continue a sequência de dimensões a partir daí.

Guarde cada resposta associada ao nome da dimensão. Ao concluir todas as dimensões, guarde o conjunto como `<publico>` no formato: `[dimensão]: [resposta], [dimensão]: [resposta], ...`

**Etapa 5 — Descrição**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Macro categoria, Categoria de mercado e Público.

Gere 3 variações de descrição em uma frase usando `<tipo>`, `<subtipo>`, `<segmento>`, `<macro>`, `<categoria>` e `<publico>` como contexto. Use `AskUserQuestion` com as 3 variações e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<descricao>`.

**Etapa 6 — Tags**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Macro categoria, Categoria de mercado, Público e Descrição.

Monte até 3 conjuntos de tags relevantes usando `<tipo>`, `<subtipo>`, `<segmento>`, `<macro>`, `<categoria>`, `<publico>` e `<descricao>` como contexto. Use `AskUserQuestion` com `multiSelect: true`, exibindo cada conjunto como opção (ex: `branding, identidade, b2b`), e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<tags>`.

**Etapa 7 — Execução**

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli new-project \
  --path "<pasta>" \
  --name "<nome>" \
  --description "<descricao>" \
  --tags "<tags>"
```

## Pós-execução

Mostre o output ao usuário.

Edite `<pasta>/project/project-details.md` preenchendo a tabela de identidade com os valores coletados:

| Campo | Valor |
|---|---|
| Tipo de projeto | `<tipo>` |
| Sub-tipo | `<subtipo>` |
| Segmento de mercado | `<segmento>` |
| Macro categoria | `<macro>` |
| Categoria de mercado | `<categoria>` |
| Público | `<publico>` |
| Palavras-chave | `<tags>` |
