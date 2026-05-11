---
name: build-resource
type: command
version: 1.1.0
status: stable

description: Cria um novo recurso no projeto atual a partir do template correspondente.
tags: [build, resource, template]

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

# /build-resource

> **Instruções de execução — siga esta sequência:**
>
> 1. Verifique se `~/.claude/hub-path` existe:
>    ```bash
>    cat ~/.claude/hub-path
>    ```
>    Se não existir, peça ao usuário para executar `/claude-start` primeiro.
>
> 2. Se o tipo não foi informado, pergunte:
>    "Qual o tipo do recurso? Opções: `skill`, `agent`, `hook`, `command`"
>
> 3. Se o nome não foi informado, pergunte:
>    "Qual o nome do recurso?"
>
> 4. Execute:
>    ```bash
>    HUB_DIR="$(cat ~/.claude/hub-path)"
>    bash "$HUB_DIR/install.sh" build-resource <tipo> <nome>
>    ```
>
> 5. Mostre o arquivo criado e oriente o usuário a preencher os placeholders antes de usar `/publish-resource`.

---

## Referência

Cria um novo recurso no projeto atual usando o template do tipo escolhido. O arquivo gerado fica em `.claude/<tipo>s/<nome>` com frontmatter pré-preenchido e corpo com placeholders para preencher.

### Tipos disponíveis

| Tipo | Destino |
|---|---|
| `skill` | `.claude/skills/<nome>.md` |
| `agent` | `.claude/agents/<nome>.md` |
| `hook` | `.claude/hooks/<nome>/hook.json` + `hook.sh` |
| `command` | `.claude/commands/<nome>.md` |
