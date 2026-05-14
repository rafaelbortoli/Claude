---
# about
id: cmd-009
name: setup-claude
type: command
project: ""
description: Configura o CLAUDE.md do projeto com identidade, stack e campos de contexto para smart-suggestions.
tags: [setup, claude, project]

# history
author: ""
created: 2026-05-14
status: stable
version: 1.1.0
updated: 2026-05-14

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /setup-claude

Configura o `CLAUDE.md` e completa `project/project-details.md` com os campos de identidade do projeto.

Executar uma vez por repositório após `/new-project` — pode ser re-executado com segurança (idempotente).

---

## Passo 1 — Verificar hub-path

```bash
cat ~/.claude/hub-path
```

Se o arquivo não existir, informe: _"Execute `/claude-start` primeiro para configurar o hub."_ e encerre.

## Passo 2 — Caminho do projeto

Execute:

```bash
pwd
```

**[smart-suggestions: on]** Sugestões de caminho baseadas no diretório atual e pastas irmãs.

Antes de perguntar:
1. Use o caminho retornado por `pwd` como primeira opção
2. Liste as pastas no diretório pai e identifique até 2 pastas irmãs relevantes (que contenham `.claude/`)

Se houver pastas irmãs relevantes: use `AskUserQuestion` com até 3 caminhos e **"Outro caminho (digitar)"** como quarta opção.
Se não houver: use `AskUserQuestion` com 2 opções:
- **"Sim, usar `<caminho retornado>`"**
- **"Não, informar outro caminho"**

Se o usuário escolher "Outro": pergunte em texto livre e aguarde a resposta.

Guarde como `<projeto>`.

## Passo 3 — Nome do projeto

Pergunte em texto livre: _"Qual o nome do projeto?"_

Guarde como `<nome>`.

## Passo 4 — Executar bootstrap

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli new-project \
  --path "<projeto>" \
  --name "<nome>"
```

Mostre o output ao usuário.

---

## Passo 5 — Completar project-details.md

Leia `<projeto>/project/project-details.md`. Para cada campo que ainda estiver com placeholder ou em branco, faça a pergunta correspondente abaixo. Pule os campos já preenchidos.

**Tipo de projeto** — use `AskUserQuestion`:
- **"Branding"** — identidade visual e marca
- **"UX and UI"** — research, interfaces e design system
- **"Product Design"** — design estratégico de produto

**Sub-tipo (condicional ao Tipo):**

Se **Branding**: use `AskUserQuestion`: Plus / Pro / Ultra
Se **UX and UI**: use `AskUserQuestion` com `multiSelect: true`: UX Research / Interface digital / Design System / Outro (digitar)
Se **Product Design**: use `AskUserQuestion`: New product / Feature / Redesign

**Mercado** — use `AskUserQuestion`:
- **"Financeiro"** — pagamentos, crédito, seguros, banking
- **"Saúde & Bem-estar"** — healthtech, wellness, fitness
- **"Educação & Conteúdo"** — edtech, e-learning, mídia
- **"Tecnologia & SaaS"** — plataforma, API, marketplace

**Segmento (condicional ao Mercado):**

Se **Financeiro**: Pagamentos & Crédito / Seguros & Banking / Investimentos & Wealth / Outro
Se **Saúde & Bem-estar**: Saúde digital & Telemedicina / Bem-estar & Fitness / Farmácia & Medicamentos / Outro
Se **Educação & Conteúdo**: Edtech & E-learning / Mídia & Entretenimento / Conteúdo & Comunicação / Outro
Se **Tecnologia & SaaS**: Plataforma & SaaS / Marketplace & E-commerce / API & Infraestrutura / Outro

Use `AskUserQuestion` em cada caso (3 fixas + "Outro (digitar)").

**Público-alvo** — use `AskUserQuestion`:
- **"Pessoa física"** — indivíduo em contexto pessoal
- **"Profissional / Empresa"** — contexto de trabalho
- **"Especialista"** — expertise técnica ou de domínio
- **"Interno"** — colaboradores da organização

**Perfil do público (condicional ao Público-alvo):**

Se **Pessoa física**: Público geral / Público jovem / Público sênior / Outro
Se **Profissional / Empresa**: Autônomo / Pequeno negócio / Empresa de médio porte / Enterprise / Outro
Se **Especialista**: Desenvolvedor / Técnico / Profissional de saúde / Educador / Pesquisador / Outro
Se **Interno**: Operações / Suporte / Comercial / Marketing / Vendas / Gestão / Liderança / Outro

Use `AskUserQuestion` em cada caso (3 fixas + "Outro (digitar)").

**Palavras-chave** — pergunte em texto livre:
_"Quais palavras-chave descrevem este produto? (ex: pagamentos, recorrência, split)"_

Após coletar, edite `project-details.md` preenchendo todos os campos coletados.

---

## Passo 6 — Visão Geral do CLAUDE.md

Leia `<projeto>/.claude/CLAUDE.md`. Se a seção `## Visão Geral` **já estiver preenchida**, pule este passo.

Se estiver vazia ou com placeholder, pergunte em texto livre:
_"Visão Geral: descreva em uma frase o que este projeto faz e seu objetivo principal."_

Edite o CLAUDE.md substituindo o placeholder pela resposta. Atualize também o campo `description` no frontmatter.

---

## Passo 7 — Confirmar

Mostre ao usuário o `project-details.md` final e confirme que o projeto está configurado.
