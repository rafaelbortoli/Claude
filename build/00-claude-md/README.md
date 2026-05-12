---
# about
name: build-claude-md-readme
type: readme
project: ""
description: Documentação do layer 00 — templates e fragments para CLAUDE.md.
tags: [claude-md, build]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.0.0
updated: ""

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# 00 — CLAUDE.md

Templates para a constituição do agente. Primeiro layer — sempre carregado.

## Arquivos

```
00-claude-md/
├── global.md          # Composição completa — instalar em ~/.claude/CLAUDE.md
├── project.md         # Template minimalista — instalar em .claude/CLAUDE.md do projeto
└── fragments/         # Blocos de construção de global.md
    ├── language.md
    ├── communication.md
    ├── execution.md
    ├── tools.md
    └── anti-hallucination.md
```

## Relação entre fragments e global.md

Os fragments são a fonte autoritativa de cada seção. O `global.md` é o output composto — reúne todos os fragments em um único arquivo pronto para instalar.

Ao alterar uma regra: editar o fragment correspondente e sincronizar o `global.md`.

## Dois escopos

| Arquivo | Destino | Conteúdo |
|---|---|---|
| `global.md` | `~/.claude/CLAUDE.md` | Regras universais: idioma, comunicação, execução, ferramentas, stack de referência |
| `project.md` | `.claude/CLAUDE.md` | Contexto específico: arquitetura, convenções, mapa do repo, restrições |

O projeto-específico estende o global — não o substitui.

## Como usar

**Novo ambiente:**
```bash
cp build/00-claude-md/global.md ~/.claude/CLAUDE.md
```

**Novo projeto:**
```bash
cp build/00-claude-md/project.md .claude/CLAUDE.md
# preencher os placeholders
```
