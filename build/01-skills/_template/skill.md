---
# identity
name: skill-name
type: skill
version: 1.0.0
status: draft

# context
# description: frase objetiva — o Claude usa este campo para decidir quando invocar a skill
description: (preencher)
tags: []

# loading
scope: project
auto_load: false

# traceability — preenchidos pelo install.sh
source: ""
project: ""
dependencies: []
checksum: ""

# metadata
author: ""
created: ""
updated: ""
---

# [Nome da Skill]

## O que faz

<!-- Uma frase descrevendo a responsabilidade única desta skill. -->

## Quando usar

<!-- Contextos que devem ativar esta skill. O Claude lê esta seção para decidir se a skill é relevante.
     Seja específico para evitar falsos positivos.
     Exemplo:
     - Quando o usuário pedir revisão antes de abrir um PR
     - Quando houver mudanças em arquivos que cruzam camadas arquiteturais
-->

## Não usar quando

<!-- Contextos onde esta skill não se aplica.
     Exemplo:
     - Arquivos de configuração ou fixtures
     - Alterações apenas em comentários ou documentação
-->

## Instruções

<!-- Passos que o Claude segue ao executar esta skill.
     Seja prescritivo: liste ações, critérios e formato de output.
     Siga o protocolo de execução do CLAUDE.md — não tome ações irreversíveis sem aprovação.

     Exemplo:
     1. Ler os arquivos indicados
     2. Verificar critério A
     3. Verificar critério B
     4. Reportar no formato: [PASS/FAIL] — justificativa
-->

## Output

<!-- Formato exato do que a skill entrega.
     Exemplo:
     - Relatório em markdown com itens aprovados e reprovados
     - Nenhuma alteração de arquivo — apenas análise
-->

## Referências

<!-- Arquivos e documentação que a skill deve consultar.
     Incluir sempre:
     - `.claude/CLAUDE.md` — convenções e restrições do projeto
     Adicionar conforme necessário:
     - `docs/guidelines/<arquivo>.md`
-->
