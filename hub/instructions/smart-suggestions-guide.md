---
# about
name: smart-suggestions-guide
type: instruction
project: ""
description: Convenção smart-suggestions — como usar o toggle de sugestões inteligentes em command.md.
tags: [smart-suggestions, commands, conventions]

# history
author: ""
created: 2026-05-14
status: stable
version: 1.0.0
updated: 2026-05-14

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Smart-suggestions — Guia de Convenção

Padrão do hub para perguntas inteligentes em comandos. Cada pergunta em um `command.md` pode declarar se usa sugestões geradas por contexto.

---

## O toggle

```markdown
**[smart-suggestions: on]** Descrição da pergunta.
```

```markdown
**[smart-suggestions: off]** Descrição da pergunta.
```

- `on` — Claude lê o contexto, gera até 3 opções e apresenta via `AskUserQuestion` com "Outro (digitar)" como quarta opção
- `off` (ou ausente) — pergunta direta em texto livre, sem geração de sugestões

O toggle é por pergunta — não é global. Uma pergunta complexa pode ter `on` enquanto uma simples mantém `off`.

---

## Regras de uso

### Limite de opções

`AskUserQuestion` suporta no máximo 4 opções. A quarta é sempre reservada para "Outro (digitar)". Portanto, smart-suggestions gera no máximo **3 sugestões**.

Se não houver sugestões suficientes (mínimo 1), fazer a pergunta em texto livre — nunca exibir `AskUserQuestion` com opções vazias.

### Fluxo após "Outro (digitar)"

Quando o usuário seleciona "Outro (digitar)", Claude faz a pergunta original em texto livre no chat e aguarda a resposta. Não abre nova rodada de `AskUserQuestion`.

### Quando não usar smart-suggestions (`off`)

- Confirmações (Sim/Cancelar): opções fixas, não há contexto a gerar
- Listas com mais de 4 opções pré-definidas: usar lista ou tabela no lugar de `AskUserQuestion`
- Perguntas sem contexto interpretável para gerar sugestões úteis

---

## Fontes de contexto por tipo de pergunta

| Tipo de pergunta | Fontes de contexto |
|---|---|
| Caminho do projeto | `pwd`, pastas irmãs no mesmo nível |
| Nome do recurso | Recursos instalados em `.claude/skills/`, `.claude/agents/`, `.claude/commands/` |
| Descrição do recurso | Frontmatter + corpo do arquivo sendo processado |
| Tags do recurso | `CLAUDE.md` (domain, project_type, audience, keywords), tags de outros recursos |

---

## Campos do CLAUDE.md que alimentam sugestões

Preenchidos via `/new-project`. Sem esses campos, as sugestões degradam graciosamente para o conteúdo do arquivo.

| Campo | Tipo | Exemplo | Usado para |
|---|---|---|---|
| `domain` | string | `fintech` | Tags de domínio |
| `project_type` | string | `saas` | Categoria do recurso |
| `audience` | string | `b2b` | Tags de audiência |
| `stage` | string | `mvp` | Calibra tom das sugestões |
| `keywords` | lista | `[pagamentos, split]` | Seeds para tags e descrições |

```yaml
# system
domain: fintech
project_type: saas
audience: b2b
stage: mvp
keywords: [pagamentos, recorrência, split]
```

---

## Checklist para novos command.md

Ao criar um novo comando, avalie cada pergunta:

- [ ] **Caminho do projeto** → `on` (sugerir pwd + irmãs)
- [ ] **Nome do recurso** → `on` (sugerir baseado em padrão existente)
- [ ] **Descrição** → `on` (sugerir baseado no conteúdo do arquivo)
- [ ] **Tags** → `on` (sugerir conjuntos por categoria)
- [ ] **Tipo do recurso** (lista fixa > 4) → lista ou tabela, sem toggle
- [ ] **Confirmações** (Sim/Cancelar) → `off` ou omitir, usar opções fixas

---

## Exemplo completo em command.md

```markdown
## Passo 3 — Nome do recurso

**[smart-suggestions: on]** Sugestões de nome baseadas nos recursos já instalados.

Antes de perguntar:
1. Liste os recursos instalados em `.claude/skills/`, `.claude/agents/`, `.claude/commands/`
2. Identifique o padrão de nomenclatura (ex: `ux-writing-review` → padrão `<domínio>-<ação>`)
3. Gere até 3 sugestões que seguem o mesmo padrão, baseadas no tipo sendo criado

Se houver pelo menos 1 sugestão: use `AskUserQuestion` com as sugestões e "Outro (digitar)" como quarta opção.
Se não houver recursos instalados: pergunte em texto livre.

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.
```
