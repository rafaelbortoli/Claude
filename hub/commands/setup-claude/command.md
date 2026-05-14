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

Leia `<projeto>/project/project-details.md`. Preencha os campos ainda em branco na tabela de identidade:

**Domínio** — mercado de negócio do projeto.

Exiba como lista numerada e aguarde o usuário informar o número:

1. fintech — serviços financeiros, pagamentos, crédito
2. edtech — educação, cursos, aprendizado
3. healthtech — saúde, bem-estar, telemedicina
4. e-commerce — varejo e marketplace de produtos
5. saas-horizontal — ferramenta sem vertical específica
6. Outro (digitar)

---

**Público-alvo** — use `AskUserQuestion`:
- **"b2b"** — empresas e times
- **"b2c"** — consumidores finais
- **"developers"** — times técnicos
- **"equipe-interna"** — uso interno da empresa

---

**Estágio** — use `AskUserQuestion`:
- **"mvp"** — primeira versão, validando hipóteses
- **"beta"** — produto funcional em teste com usuários reais
- **"producao"** — produto lançado e em operação

---

**Palavras-chave** — pergunte em texto livre:
_"Quais palavras-chave descrevem este produto? (ex: pagamentos, recorrência, split)"_

---

## Passo 6 — Visão Geral do CLAUDE.md

Leia `<projeto>/.claude/CLAUDE.md`. Se a seção `## Visão Geral` estiver vazia ou com placeholder:

Pergunte em texto livre: _"Visão Geral: descreva em uma frase o que este projeto faz e seu objetivo principal."_

Edite o CLAUDE.md substituindo o placeholder pela resposta. Atualize também o campo `description` no frontmatter.

---

## Passo 7 — Escrever project-details.md

Edite `<projeto>/project/project-details.md` preenchendo a tabela de identidade com todos os valores coletados.

## Passo 8 — Confirmar

Mostre ao usuário o `project-details.md` final e confirme que o projeto está configurado.
