---
# identity
name: fragment-frontmatter
type: fragment
version: 1.0.0
status: stable

# context
description: Padrão de frontmatter YAML — campos obrigatórios, valores aceitos e regras de uso para todos os recursos.
tags: [frontmatter, standard, metadata]

# loading
scope: global
auto_load: false

# traceability — preenchidos pelo install.sh
source: ""
project: ""
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: ""
---

## Padrão de Frontmatter

Todo arquivo de recurso (skill, agent, hook, plugin, command, instruction) deve ter frontmatter YAML completo no topo do arquivo.

### Campos obrigatórios

```yaml
# identity
name: resource-name           # nome legível em kebab-case
type: skill                   # tipo do recurso (ver valores aceitos abaixo)
version: 1.0.0                # semântico: major.minor.patch
status: draft                 # ciclo de vida (ver valores aceitos abaixo)

# context
description: ""               # uma frase objetiva — usada pelo Claude para correspondência
tags: []                      # lista de tags em kebab-case

# loading
scope: project                # onde o recurso é instalado (ver valores aceitos abaixo)
auto_load: false              # carregar automaticamente na sessão ou apenas sob demanda

# traceability — preenchidos pelo install.sh, não manualmente
source: ""                    # hub/<type>/<name>@<version> ou local
project: ""                   # nome do projeto onde está instalado
dependencies: []              # recursos que precisam estar instalados antes deste
checksum: ""                  # hash do conteúdo — gerado automaticamente

# metadata
author: ""
created: ""                   # YYYY-MM-DD
updated: ""                   # YYYY-MM-DD — atualizado automaticamente pelo install.sh
```

### Valores aceitos

**`type`**
`skill` | `agent` | `hook` | `plugin` | `command` | `instruction` | `doc` | `fragment` | `readme`

**`status`**
`draft` | `review` | `stable` | `deprecated`

**`scope`**
`global` — instalado em `~/.claude/`, disponível em todos os projetos
`project` — instalado em `.claude/`, disponível apenas neste repositório

### Campos gerados automaticamente

Os campos abaixo são preenchidos pelo `install.sh` — nunca preencher manualmente:

| Campo | Quando é gerado | Valor |
|---|---|---|
| `source` | No install | `hub/<type>/<name>@<version>` ou `local` |
| `project` | No install | Nome do projeto destino |
| `checksum` | No install e no publish | Hash SHA-256 do conteúdo do arquivo |
| `updated` | No install e no publish | Data da operação em `YYYY-MM-DD` |

### Regras de uso

- `auto_load: true` deve ser exceção — usar apenas para recursos que são invariavelmente necessários em toda sessão
- Recursos com `status: deprecated` não devem ser instalados em novos projetos
