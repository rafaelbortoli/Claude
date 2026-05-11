---
name: install-resource
type: command
version: 1.1.0
status: stable

description: Instala um recurso do hub no projeto atual — skill, agent, hook, command ou plugin.
tags: [install, resource, hub]

scope: global
auto_load: false

source: hub/commands/install-resource@1.1.0
project: Claude
dependencies: []
checksum: ""

author: ""
created: 2026-05-10
updated: 2026-05-10
---

# /install-resource

> **Instruções de execução — siga esta sequência:**
>
> 1. Verifique se `~/.claude/hub-path` existe:
>    ```bash
>    cat ~/.claude/hub-path
>    ```
>    Se não existir, peça ao usuário para executar `/claude-start` primeiro.
>
> 2. Se o tipo não foi informado, pergunte:
>    "Qual o tipo do recurso? Opções: `skill`, `agent`, `hook`, `command`, `plugin`"
>
> 3. Se o nome não foi informado, pergunte:
>    "Qual o nome do recurso?"
>
> 4. Execute:
>    ```bash
>    HUB_DIR="$(cat ~/.claude/hub-path)"
>    bash "$HUB_DIR/install.sh" install-resource <tipo> <nome>
>    ```
>
> 5. Se o script perguntar sobre conflito de versão (`[s] sobrescrever [p] pular [c] cancelar`), repasse a pergunta ao usuário e responda com a escolha dele.
>
> 6. Mostre a saída e confirme o que foi instalado.

---

## Referência

Instala um recurso publicado no hub dentro do projeto atual.

### Tipos disponíveis

| Tipo | Destino |
|---|---|
| `skill` | `.claude/skills/<nome>.md` |
| `agent` | `.claude/agents/<nome>.md` |
| `hook` | `.claude/hooks/<nome>/hook.json` + `hook.sh` |
| `command` | `.claude/commands/<nome>.md` |
| `plugin` | instala todos os recursos do plugin em sequência |

### Flags

```
--dry-run   mostra o que seria feito sem executar
```
