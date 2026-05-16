---
# identity
name: hub-skills-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo de skills — conhecimento especializado ativado on-demand pelo Claude.
tags: [hub, skills]

# loading
scope: global
auto_load: false

# traceability
source: ""
project: ""
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: ""
---

# Hub — Skills

Conhecimento especializado ativado on-demand. O Claude infere quando invocar cada skill com base na descrição e nos triggers definidos.

## Estrutura de cada skill

```
<skill-name>/
├── skill.json       # Metadados: nome, versão, triggers, tags, scope
├── skill.md         # Conteúdo: instruções que o Claude executa
├── scripts/         # Scripts shell que a skill invoca (se houver)
├── templates/       # Boilerplate que a skill copia para o projeto (se houver)
└── assets/          # Arquivos de suporte (se houver)
```

## Instalação

**Global** — disponível em todos os projetos:
```bash
cp -r hub/skills/<nome> ~/.claude/skills/
```

**Por projeto** — disponível apenas neste repositório:
```bash
cp -r hub/skills/<nome> .claude/skills/
```

## Skills disponíveis

<!-- Esta seção é atualizada a cada novo recurso publicado no hub. -->

| Nome | Descrição | Scope | Tags |
|---|---|---|---|
| — | — | — | — |
