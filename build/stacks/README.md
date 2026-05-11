---
name: build-stacks-readme
type: readme
version: 1.0.0
status: stable

description: Índice das stacks disponíveis para setup de projetos.
tags: [build, stacks, readme]

scope: global
auto_load: false

source: ""
project: ""
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: ""
---

# Build — Stacks

Cada stack define quais plugins e instruções são instalados por padrão no `setup-claude`.

| Stack | Descrição |
|---|---|
| `nextjs-supabase` | Next.js + Tailwind + Supabase |
| `generic` | Sem stack definida — apenas recursos universais |

## Estrutura de uma stack

```json
{
  "name": "nextjs-supabase",
  "description": "...",
  "version": "1.0.0",
  "technologies": ["nextjs", "tailwind", "supabase", "typescript"],
  "plugins": [],
  "instructions": []
}
```

- `plugins` — lista de plugins do hub instalados automaticamente
- `instructions` — fragmentos de instrução incluídos no CLAUDE.md do projeto
