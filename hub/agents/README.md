---
# identity
name: hub-agents-readme
type: readme
version: 1.0.0
status: stable

# context
description: Catálogo de agents — subagentes especializados com contexto isolado.
tags: [hub, agents]

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

# Hub — Agents

Subagentes especializados com contexto próprio. Cada agente tem responsabilidade única e retorna uma única mensagem ao agente principal.

## Estrutura de cada agente

```
<agent-name>/
├── agent.json       # Metadados: nome, versão, ferramentas, escopo, retorno
└── agent.md         # Definição: responsabilidade, instruções, formato de output
```

## Como invocar

```
Agent({
  description: "descrição curta da tarefa",
  subagent_type: "general-purpose",
  prompt: "Conteúdo autocontido — inclua tudo que o agente precisa saber."
})
```

O agente não tem memória da sessão principal. O prompt deve ser autocontido.

## Agents disponíveis

<!-- Esta seção é atualizada a cada novo recurso publicado no hub. -->

| Nome | Responsabilidade | Ferramentas | Tags |
|---|---|---|---|
| — | — | — | — |
