---
name: claude-start
type: command
version: 1.1.0
status: stable

description: Setup global do Claude Code na máquina — copia CLAUDE.md e settings.json para ~/.claude/.
tags: [setup, global, machine]

scope: global
auto_load: false

source: ""
project: ""
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: 2026-05-10
---

# /claude-start

> **Instruções de execução — siga esta sequência:**
>
> 1. Verifique se `~/.claude/hub-path` existe:
>    ```bash
>    cat ~/.claude/hub-path
>    ```
>    Se não existir, informe: "hub-path não encontrado. Execute o instalador manualmente:
>    `bash <caminho-do-repositório>/install.sh claude-start`"
>
> 2. Se existir, execute:
>    ```bash
>    HUB_DIR="$(cat ~/.claude/hub-path)"
>    bash "$HUB_DIR/install.sh" claude-start
>    ```
>
> 3. Mostre a saída ao usuário e confirme o que foi instalado ou mantido.

---

## Referência

Configura o ambiente global do Claude Code na máquina. Executar uma única vez por máquina — pode ser re-executado com segurança (idempotente).

Copia os arquivos globais para `~/.claude/`, sem sobrescrever arquivos existentes:

```
global/CLAUDE.md     → ~/.claude/CLAUDE.md      (apenas se não existir)
global/settings.json → ~/.claude/settings.json   (apenas se não existir)
```

Também salva `~/.claude/hub-path` com o caminho do repositório, necessário para os demais comandos.
