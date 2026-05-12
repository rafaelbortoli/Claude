---
# about
name: build-agents-readme
type: readme
project: ""
description: Documentação do layer 03 — templates para criação de agentes.
tags: [agents, build]

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

# 03 — Agents

Templates para criação de agentes. Agentes concluídos vão para `hub/agents/`.

## O que são agentes

Subagentes com contexto próprio, isolados da sessão principal. Em vez de o Claude assumir um papel, um agente especializado é invocado para uma tarefa específica e retorna apenas o resultado.

## Modelo mental

```
Sessão principal                      Agente
──────────────────                    ──────────────────────
Planeja o trabalho       →  spawn     Recebe prompt autocontido
Chama o agente                        Executa com ferramentas próprias
Permanece limpa          ←  retorno   Retorna UMA mensagem
Vê apenas o resultado
```

## Princípios

- **Responsabilidade única**: cada agente faz uma coisa. Se precisar de dois papéis, crie dois agentes.
- **Prompt autocontido**: o agente não tem memória da sessão principal. Tudo necessário deve estar no prompt de invocação.
- **Uma mensagem de retorno**: o agente nunca pergunta, nunca pede confirmação — entrega o resultado e encerra.
- **Ferramentas mínimas**: o template padrão concede `Read` e `Bash`. Adicionar `Edit` ou `Write` apenas quando a tarefa exige escrita explícita.

## Estrutura de um agente

```
<agent-name>/
├── agent.json     # Metadados: nome, versão, ferramentas, escopo, retorno
└── agent.md       # Definição: responsabilidade, instruções, output, invocação
```

## Responsabilidade de cada arquivo

| Arquivo | Lido por | Contém |
|---|---|---|
| `agent.json` | `registry.json`, `install.sh` | Metadados completos: ferramentas, escopo, tags |
| `agent.md` | Claude (sessão principal) | Instruções de invocação e formato de output |

## Campos de agent.json

| Campo | Descrição |
|---|---|
| `name` | Identificador em kebab-case |
| `version` | Semântico: `1.0.0` |
| `description` | Responsabilidade única — uma frase |
| `tools` | Ferramentas disponíveis — começar com o mínimo (`Read`, `Bash`) |
| `scope.does` | O que o agente executa |
| `scope.does_not` | Limites explícitos |
| `returns` | Formato e conteúdo do retorno |

## Ferramentas disponíveis

| Ferramenta | Quando conceder |
|---|---|
| `Read` | Sempre que o agente precisar ler arquivos |
| `Bash` | Comandos de busca, análise, execução de testes |
| `Edit` | Apenas quando a tarefa exige edição de arquivos |
| `Write` | Apenas quando a tarefa exige criação de arquivos |
| `WebSearch` | Pesquisa externa |
| `WebFetch` | Leitura de URLs |
| `Agent` | Sub-delegação — evitar salvo casos justificados |

## Como criar um novo agente

1. Copiar `_template/` para uma nova pasta com o nome em kebab-case
2. Preencher `agent.json` — definir ferramentas com o mínimo necessário
3. Preencher `agent.md` — `description` deve ser idêntica ao `agent.json`
4. Testar a invocação no Claude Code
5. Mover a pasta concluída para `hub/agents/<agent-name>/`
6. Atualizar `registry.json` na raiz do repositório
