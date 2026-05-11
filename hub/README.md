---
# identity
name: hub-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo central de recursos Claude finalizados — skills, agents, hooks, plugins e instructions.
tags: [hub, catalog]

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

# Hub — Catálogo de Recursos

Repositório central de todos os recursos desenvolvidos para o Claude. Recursos aqui são finalizados, testados e prontos para uso.

## Estrutura

```
hub/
├── skills/          Conhecimento on-demand, ativado por contexto
├── agents/          Subagentes especializados com contexto isolado
├── hooks/           Scripts determinísticos que disparam em eventos
├── instructions/    Fragmentos reutilizáveis de CLAUDE.md
└── plugins/         Bundles instaláveis que agrupam recursos acima
```

## Fluxo de entrada

```
build/_template/ → desenvolver → testar → hub/<tipo>/<nome>/
```

Nenhum recurso entra no hub sem ter sido desenvolvido a partir de um template em `build/` e testado no Claude Code.

## Como encontrar um recurso

- **Por tipo**: navegar na pasta correspondente (`skills/`, `agents/`, etc.)
- **Por tag ou stack**: consultar `registry.json` na raiz do repositório
- **Por texto**: `grep -r "palavra" hub/`

## Como instalar um recurso em um projeto

```bash
# Instalar um plugin completo
./install.sh --plugin <nome>

# Instalar um recurso individual
./install.sh --skill <nome>
./install.sh --agent <nome>
./install.sh --hook <nome>
```

## Convenções

- Cada recurso vive em sua própria pasta com nome em kebab-case
- Todo recurso tem um arquivo de metadados (`skill.json`, `agent.json`, `hook.json`, `plugin.json`)
- Versioning semântico: incrementar `version` a cada alteração publicada
- Alterações em recursos existentes devem ser testadas antes de atualizar no hub
