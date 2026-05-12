---
# about
name: fragment-tools
type: fragment
project: ""
description: Regras de uso de ferramentas — hierarquia, paralelismo, Bash e invocação de agentes.
tags: [tools, bash, agents, parallelism]

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

## Uso de Ferramentas

### Hierarquia de Ferramentas

1. Ferramentas dedicadas têm prioridade sobre Bash (Read, Edit, Write)
2. Bash apenas para operações exclusivas de shell
3. Agent para delegação de tarefas que poluiriam o contexto principal

### Regras de Arquivo

- Leitura: sempre usar `Read`, nunca `cat` / `head` / `tail`
- Edição: sempre usar `Edit` para arquivos existentes
- Criação: usar `Write` apenas para arquivos novos ou reescrita completa
- Nunca usar `echo >` ou `cat <<EOF` para escrever arquivos

### Paralelismo

- Chamadas independentes de ferramentas devem ser feitas em paralelo na mesma mensagem
- Chamadas dependentes devem ser sequenciais — nunca usar placeholders ou adivinhar valores intermediários

### Bash

- Sempre usar paths absolutos
- Caminhos com espaços entre aspas duplas
- Nunca usar flags interativas (`-i`) em comandos git ou outros
- Preferir `find .` ao invés de `find /` para evitar varredura completa do sistema

### Agentes

- Usar para exploração ampla que consumiria mais de 3 queries no contexto principal
- Passar contexto suficiente no prompt — o agente não tem memória da sessão atual
- Não delegar síntese — apenas pesquisa e execução
