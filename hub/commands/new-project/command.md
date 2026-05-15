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
version: 1.3.0
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

Se o usuário escolher **0** ou **"Voltar"**: limpe `<segmento>` e retorne à Etapa 3B.

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

Se o usuário escolher **0** ou **"Voltar"**: limpe `<segmento>`, `<macro>` e retorne à Etapa 3B.

Guarde a escolha como `<categoria>`.

**Etapa 3E — Público-alvo**

Use `AskUserQuestion`:
- **"Pessoa física"** — indivíduo usando em contexto pessoal
- **"Profissional / Empresa"** — pessoa ou time usando no contexto de trabalho
- **"Especialista"** — perfil com expertise técnica ou de domínio específico
- **"Interno"** — colaboradores da organização que criou o produto

Aguarde a resposta do usuário. Guarde como `<publico>`.

**Etapa 3F — Perfil do público (condicional)**

Se `<publico>` for **Pessoa física**: use `AskUserQuestion`:
- **"Público geral"** — sem nicho definido
- **"Público jovem"** — nativos digitais, até ~30 anos
- **"Público sênior"** — 50+, foco em simplicidade e acessibilidade
- **"Outro (digitar)"** — perfil personalizado

Se `<publico>` for **Profissional / Empresa**: use `AskUserQuestion`:
- **"Autônomo / Pequeno negócio"** — MEI, freelancer, microempresa
- **"Empresa de médio porte"** — times estruturados
- **"Enterprise"** — grandes corporações
- **"Outro (digitar)"** — perfil personalizado

Se `<publico>` for **Especialista**: use `AskUserQuestion`:
- **"Desenvolvedor / Técnico"** — engenharia, dados, infra
- **"Profissional de saúde"** — médicos, enfermeiros, cuidadores
- **"Educador / Pesquisador"** — professores, tutores, cientistas
- **"Outro (digitar)"** — perfil personalizado

Se `<publico>` for **Interno**: use `AskUserQuestion`:
- **"Operações / Suporte"**
- **"Comercial / Marketing / Vendas"**
- **"Gestão / Liderança"**
- **"Outro (digitar)"** — perfil personalizado

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Aguarde a resposta do usuário. Guarde como `<perfil>`.

**Etapa 4 — Descrição**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Macro categoria, Categoria de mercado, Público-alvo e Perfil.

Gere 3 variações de descrição em uma frase usando `<tipo>`, `<subtipo>`, `<segmento>`, `<macro>`, `<categoria>`, `<publico>` e `<perfil>` como contexto. Use `AskUserQuestion` com as 3 variações e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<descricao>`.

**Etapa 5 — Tags**

**[smart-suggestions: on]** Sugestões baseadas no Tipo, Sub-tipo, Segmento, Macro categoria, Categoria de mercado, Público-alvo, Perfil e Descrição.

Monte até 3 conjuntos de tags relevantes usando `<tipo>`, `<subtipo>`, `<segmento>`, `<macro>`, `<categoria>`, `<publico>`, `<perfil>` e `<descricao>` como contexto. Use `AskUserQuestion` com `multiSelect: true`, exibindo cada conjunto como opção (ex: `branding, identidade, b2b`), e **"Outro (digitar)"** como quarta opção.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<tags>`.

**Etapa 6 — Execução**

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
| Público-alvo | `<publico>` |
| Perfil do público | `<perfil>` |
| Palavras-chave | `<tags>` |
