---
# about
name: agent-name
type: agent
project: ""
# description: responsabilidade única deste agente — uma frase objetiva
description: (preencher)
tags: []

# history
author: ""
created: ""
status: draft
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# [Nome do Agente]

## Responsabilidade

<!-- Uma frase definindo a responsabilidade única deste agente.
     Escopo fechado — se precisar fazer mais de uma coisa, crie dois agentes. -->

## Escopo

### Faz
<!-- Liste o que este agente executa.
     Exemplo:
     - Lê arquivos do projeto e mapeia dependências entre módulos
     - Retorna um relatório estruturado com achados
-->

### Não faz
<!-- Liste os limites explícitos.
     Exemplo:
     - Não edita arquivos
     - Não toma decisões de arquitetura
     - Não chama outros agentes
-->

## Contexto esperado no prompt

<!-- O agente não tem memória da sessão principal — tudo necessário deve estar no prompt.
     Descreva o que o prompt de invocação precisa conter.
     Exemplo:
     - Caminho absoluto do repositório
     - Objetivo específico da análise
     - Critérios de avaliação
-->

## Instruções

<!-- Passos prescritivos que o agente segue ao executar.
     Liste ações, critérios e condições de parada.
     Exemplo:
     1. Ler os arquivos indicados no prompt
     2. Identificar imports e dependências externas
     3. Mapear quais módulos dependem de quais
     4. Sinalizar dependências circulares
     5. Retornar o relatório no formato definido abaixo
-->

## Output

<!-- Formato exato do que o agente retorna — uma única mensagem.
     Defina estrutura, campos e exemplos.
     Nunca retornar mais de uma mensagem. Nunca pedir confirmação ao usuário.

     Exemplo:
     Relatório em markdown com:
     - Lista de módulos e suas dependências
     - Dependências circulares identificadas (se houver)
     - Sumário em uma frase
-->

## Invocação

<!-- Prompt mínimo para chamar este agente a partir da sessão principal.
     Exemplo:

     Agent({
       description: "Mapeamento de dependências do módulo X",
       subagent_type: "general-purpose",
       prompt: `
         Mapeie as dependências do módulo src/domain/.
         Repositório: /Users/.../projeto
         Retorne relatório em markdown conforme agent.md.
       `
     })
-->
