---
# identity
name: hub-instructions-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo de instructions — fragmentos reutilizáveis para composição de CLAUDE.md.
tags: [hub, instructions]

# loading
scope: global
auto_load: false

# traceability — preenchidos pelo install.sh
source: ""
project: ""
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: ""
---

# Hub — Instructions

Fragmentos reutilizáveis de CLAUDE.md. Blocos de instrução que podem ser compostos em qualquer `CLAUDE.md` global ou de projeto.

## Diferença em relação a skills

| | Instruction | Skill |
|---|---|---|
| Carregamento | Sempre ativo — faz parte do CLAUDE.md | On-demand — ativado por contexto |
| Uso | Regras, restrições, convenções permanentes | Conhecimento especializado temporário |
| Instalação | Colado diretamente no CLAUDE.md | Copiado para `.claude/skills/` |

## Estrutura de cada instruction

```
<instruction-name>.md    # Fragmento pronto para copiar no CLAUDE.md
```

## Como usar

Copiar o conteúdo do fragmento diretamente no `~/.claude/CLAUDE.md` (global) ou `.claude/CLAUDE.md` (projeto), na seção correspondente.

## Instructions disponíveis

<!-- Esta seção é atualizada a cada novo recurso publicado no hub. -->

| Nome | Descrição | Escopo recomendado |
|---|---|---|
| — | — | — |
