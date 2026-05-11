---
# identity
name: test-publish
type: command
version: 1.0.1
status: draft

# context
# description: o que o comando faz — usado pelo Claude e pelo usuário para descoberta
description: Comando de teste para validar o fluxo de publicação
tags: []

# loading
scope: project
auto_load: false

# traceability — preenchidos pelo install.sh
source: local
project: Claude
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-11
updated: ""
---

# /test-publish

## O que faz

<!-- Uma frase descrevendo o que este comando executa quando invocado. -->

## Quando usar

<!-- Contexto em que o usuário deve chamar este comando.
     Exemplo: antes de abrir um PR, após implementar uma feature, ao iniciar um novo projeto.
-->

## Argumentos

<!-- Descreva os argumentos aceitos via $ARGUMENTS, se houver.
     Exemplo:
     - `$ARGUMENTS` — caminho do arquivo ou módulo a ser analisado (opcional)
     Remover esta seção se o comando não aceitar argumentos.
-->

## Instruções

<!-- Passos que o Claude executa ao receber este comando.
     Seguir o protocolo de execução do CLAUDE.md:
     - Apresentar plano e aguardar aprovação antes de executar sequências de ações
     - Executar apenas o que está no escopo deste comando
     - Confirmar antes de qualquer ação irreversível

     Exemplo:
     1. Ler os arquivos alterados desde o último commit
     2. Invocar o agente `code-reviewer` com contexto autocontido
     3. Reportar os resultados no chat
-->

## Output

<!-- Formato e conteúdo do que o comando entrega ao usuário. -->

## Referências

<!-- Arquivos e documentação que o comando deve consultar.
     Incluir sempre:
     - `.claude/CLAUDE.md` — convenções e restrições do projeto
-->
