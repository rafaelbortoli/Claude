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
version: 1.8.0
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

## Configuração do fluxo

Execute antes de iniciar as etapas:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/onboarding-flow.json"
```

Use as configurações retornadas como fonte de verdade para cada etapa: `input_type`, `smart_suggestions`, `ui_claude` e `back`. As instruções abaixo refletem essas configurações — se houver divergência, o arquivo JSON prevalece.

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

**[smart-suggestions: on]** Derive o nome sugerido a partir do nome da pasta `<pasta>` (ex: `/Users/ana/Code/MeuApp` → `MeuApp`). Use `AskUserQuestion` com 2 opções:
- **"`<nome sugerido>`"** — usa o nome derivado da pasta
- **"Informar outro nome"** — solicita o nome em texto livre

Se o usuário escolher "Informar outro nome": pergunte em texto livre e aguarde a resposta.

Guarde como `<nome>`.

**Etapa 3 — Tipo de projeto**

Use `AskUserQuestion`:
- **"Branding"** — identidade visual e marca
- **"UX and UI"** — research, interfaces e design system
- **"Product Design"** — design estratégico de produto

Aguarde a resposta do usuário. Guarde como `<tipo>`.

**Etapa 3.1 — Sub-tipo (condicional)**

Se `<tipo>` for **Branding**: use `AskUserQuestion`:
- **"Plus"** — pacote essencial de marca
- **"Pro"** — pacote completo de marca
- **"Ultra"** — pacote abrangente de marca
- **"Voltar"** — retorna à Etapa 3 para escolher outro tipo

Se `<tipo>` for **UX and UI**: use `AskUserQuestion` com `multiSelect: true`:
- **"UX Research"** — discovery e pesquisa com usuários
- **"Interface digital"** — app, web, site, loja, landing page
- **"Design System"** — biblioteca de componentes e tokens
- **"Voltar"** — retorna à Etapa 3 para escolher outro tipo

Se `<tipo>` for **Product Design**: use `AskUserQuestion`:
- **"New product"** — produto sendo criado do zero
- **"Feature"** — nova funcionalidade em produto existente
- **"Redesign"** — revisão e melhoria de produto existente
- **"Voltar"** — retorna à Etapa 3 para escolher outro tipo

Se o usuário escolher **"Voltar"**: retorne à Etapa 3, repita a pergunta de Tipo de projeto e aguarde nova resposta antes de prosseguir.

Aguarde a resposta do usuário. Guarde como `<subtipo>`.

**Etapa 4 — Segmento de mercado**

Use `AskUserQuestion`:
- **"B2C"** — Business to Consumer
- **"B2B"** — Business to Business
- **"B2G"** — Business to Government
- **"C2C"** — Consumer to Consumer

Aguarde a resposta do usuário. Guarde como `<segmento>`.

**Etapa 4.1 — Categoria de mercado**

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/market_segments.json"
```

A partir do resultado, extraia as categorias do segmento `<segmento>`. Exiba em texto:

```
Categorias — <segmento>:

0. Voltar (escolher outro segmento)
1. [categoria]
2. [categoria]
...
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

Extraia as categorias do novo `<segmento>` e exiba a lista novamente:

```
Categorias — <segmento>:

0. Voltar (escolher outro segmento)
1. [categoria]
2. [categoria]
...
```

Pergunte: "Escolha pelo número ou nome." Aguarde a resposta. Se o usuário escolher **0** ou **"Voltar"** novamente: use `AskUserQuestion` com as 4 opções de segmento, guarde como `<segmento>`, execute o bash, exiba as categorias e aguarde. Repita esse ciclo até o usuário escolher uma categoria válida.

Guarde a escolha como `<categoria>`.

**Etapa 5 — Público**

**[smart-suggestions: off]**

O segmento definido na Etapa 4 determina automaticamente quais dimensões de público serão usadas. Não exiba esta etapa como pergunta ao usuário — prossiga diretamente para as dimensões abaixo.

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
cat "$HUB_DIR/hub/commands/new-project/audience_segments.json"
```

A partir do resultado, extraia as dimensões do segmento `<segmento>`. Percorra cada dimensão em sequência, fazendo uma pergunta por dimensão. Não use `AskUserQuestion` — exiba todas as perguntas como lista numerada em texto puro. **Múltipla seleção permitida**: o usuário pode digitar mais de um número separado por vírgula ou "e" (ex: `1, 3` ou `1 e 2`).

**Primeira dimensão** — exiba em texto (sem opção Voltar) e aguarde resposta:

```
[nome da dimensão] — [descrição]:

1. [nome] — [referência]
2. [nome] — [referência]
3. [nome] — [referência]
4. [nome] — [referência]
```

**Demais dimensões** — exiba em texto e aguarde resposta. Voltar é sempre o **0**, exibido no início da lista:

```
[nome da dimensão] — [descrição]:

0. Voltar (→ [nome da dimensão anterior])
1. [nome] — [referência]
2. [nome] — [referência]
3. [nome] — [referência]
4. [nome] — [referência]
```

Se o usuário escolher **0** ou **"Voltar"**: descarte apenas a resposta da dimensão atual e exiba novamente a dimensão anterior, mantendo as respostas das dimensões anteriores a ela. O Voltar navega uma dimensão por vez — não reinicia o bloco público.

Guarde cada resposta associada ao nome da dimensão. Ao concluir todas as dimensões, guarde o conjunto como `<publico>` no formato: `[dimensão]: [resposta(s)], [dimensão]: [resposta(s)], ...`

**Etapa 6 — Descrição**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Categoria de mercado e Público.

Gere 3 variações de descrição em uma frase usando `<tipo>`, `<subtipo>`, `<segmento>`, `<categoria>` e `<publico>` como contexto. Use `AskUserQuestion` com as 3 variações e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<descricao>`.

**Etapa 7 — Tags**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Categoria de mercado, Público e Descrição.

Monte até 3 conjuntos de tags relevantes usando `<tipo>`, `<subtipo>`, `<segmento>`, `<categoria>`, `<publico>` e `<descricao>` como contexto. Use `AskUserQuestion` com `multiSelect: true`, exibindo cada conjunto como opção (ex: `branding, identidade, b2b`), e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<tags>`.

**Etapa 8 — Execução**

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli new-project \
  --path "<pasta>" \
  --name "<nome>" \
  --description "<descricao>" \
  --tags "<tags>" \
  --type "<tipo>" \
  --subtype "<subtipo>" \
  --segment "<segmento>" \
  --category "<categoria>" \
  --audience "<publico>"
```

## Pós-execução

Mostre o output ao usuário.
