---
# identity
name: hub-plugins-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo de plugins — bundles instaláveis que agrupam skills, agents, hooks e commands.
tags: [hub, plugins]

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

# Hub — Plugins

Bundles instaláveis que agrupam skills, agents, hooks e commands em uma capacidade coesa.

## Estrutura de cada plugin

```
<plugin-name>/
├── plugin.json      # Manifesto: nome, versão, lista de recursos, stack compatível
├── skills/          # Skills incluídas no bundle
├── agents/          # Agents incluídos no bundle
├── hooks/           # Hooks incluídos no bundle
└── commands/        # Slash-commands expostos pelo plugin
```

## Como instalar

```bash
# Em um projeto específico
./install.sh --plugin <nome>

# Global (todos os projetos)
./install.sh --plugin <nome> --global
```

## Compatibilidade de stack

A stack padrão do projeto é `nextjs-supabase-vercel-claude`. Plugins com `stack` declarado em `plugin.json` devem ser compatíveis com essa stack para serem instalados pelo bootstrap.

Plugins com `stack: []` são universais — aplicáveis a qualquer projeto.

## Plugins disponíveis

<!-- Esta seção é atualizada a cada novo recurso publicado no hub. -->

| Nome | Descrição | Stack | Tags |
|---|---|---|---|
| — | — | — | — |
