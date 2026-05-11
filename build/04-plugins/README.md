---
# identity
name: build-plugins-readme
type: readme
version: 1.0.0
status: stable

# context
description: Documentação do layer 04 — templates para criação de plugins.
tags: [plugins, build]

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

# 04 — Plugins

Templates para criação de plugins. Plugins concluídos vão para `hub/plugins/`.

## O que são plugins

Bundles que agrupam skills, agents, hooks e commands em uma unidade coesa e instalável. Um plugin representa uma capacidade completa — não um recurso isolado.

## Estrutura de um plugin

```
<plugin-name>/
├── plugin.json      # Manifesto: nome, versão, lista de recursos incluídos
├── skills/          # Cópias das skills incluídas no bundle
├── agents/          # Cópias dos agents incluídos no bundle
├── hooks/           # Cópias dos hooks incluídos no bundle
└── commands/        # Slash-commands expostos pelo plugin
```

## O que vai em cada subpasta

| Pasta | Conteúdo | Origem |
|---|---|---|
| `skills/` | Cópias completas de pastas de skills | `hub/skills/<nome>/` |
| `agents/` | Cópias completas de pastas de agents | `hub/agents/<nome>/` |
| `hooks/` | Cópias completas de pastas de hooks | `hub/hooks/<nome>/` |
| `commands/` | Arquivos `.md` de commands criados para este plugin | Criados aqui |

Plugins são self-contained — carregam cópias dos recursos, não referências. Isso garante que a instalação funcione sem depender do estado do hub.

## Diferença entre recursos e plugins

| | Recurso (skill / agent / hook) | Plugin |
|---|---|---|
| Unidade | Atômica — faz uma coisa | Composta — agrupa recursos |
| Origem | `hub/skills/`, `hub/agents/`, `hub/hooks/` | `hub/plugins/` |
| Instalação | Manual, individual | Em bloco via script |
| Uso | Referenciado por plugins | Referenciado por stacks |

## Commands vs Skills

| | Command | Skill |
|---|---|---|
| Ativação | Usuário digita `/command-name` | Claude infere pelo contexto |
| Controle | Explícito — usuário decide quando | Implícito — Claude decide quando |
| Uso típico | Fluxos de trabalho repetíveis | Conhecimento especializado on-demand |

## Campos de plugin.json

| Campo | Descrição |
|---|---|
| `name` | Identificador em kebab-case |
| `version` | Semântico: `1.0.0` |
| `description` | O que o plugin entrega como conjunto — uma frase |
| `skills` | Nomes das skills incluídas |
| `agents` | Nomes dos agents incluídos |
| `hooks` | Nomes dos hooks incluídos |
| `commands` | Nomes dos commands expostos |
| `stack` | Stacks compatíveis (ex: `["nextjs", "supabase"]`). Vazio = universal |

## Como criar um novo plugin

1. Copiar `_template/` para uma nova pasta com o nome em kebab-case
2. Preencher `plugin.json` com metadados e listas de recursos
3. Copiar recursos finalizados de `hub/` para as subpastas correspondentes
4. Criar os commands do plugin em `commands/`
5. Testar manualmente: copiar as subpastas para `.claude/` do projeto e verificar no Claude Code
6. Mover a pasta concluída para `hub/plugins/<plugin-name>/`
7. Atualizar `registry.json` na raiz do repositório

## Como criar um bom plugin

- Agrupar recursos que resolvem um problema coeso (ex: `code-quality`, `project-init`, `supabase-setup`)
- Escopo fechado e bem definido — evitar plugins genéricos demais
- Commands devem expor os fluxos principais do plugin de forma direta ao usuário
- Declarar `stack` quando o plugin for específico de uma tecnologia
