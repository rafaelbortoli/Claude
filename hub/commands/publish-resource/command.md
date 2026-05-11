---
name: publish-resource
type: command
version: 1.1.0
status: stable

description: Normaliza e publica um recurso do projeto no hub para reutilização em outros projetos.
tags: [publish, resource, hub]

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

# /publish-resource

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
>    bash "$HUB_DIR/install.sh" publish-resource <tipo> <nome>
>    ```
>
> 5. O script exibirá o diff do que será normalizado e publicado. Mostre o diff ao usuário e aguarde confirmação antes de responder ao prompt `[s/n]`.
>
> 6. Responda `s` se o usuário confirmar, `n` para cancelar.
>
> 7. Mostre a saída final confirmando o que foi publicado.

---

## Referência

Publica um recurso local no hub. Normaliza o conteúdo antes de copiar:

- Remove `project` e `source` do frontmatter
- Muda `scope: project` → `scope: global`
- Remove paths absolutos do corpo
- Substitui nome do projeto por `<project-name>`
- Bump automático de versão patch se já existe no hub

### Validação

| Nível | Campos | Comportamento |
|---|---|---|
| Bloqueante | `name`, `type`, `version`, `description` | Impede o publish |
| Aviso | `author`, `tags` | Alerta, mas permite publicar |

### Flags

```
--dry-run   mostra diff sem aplicar
```
