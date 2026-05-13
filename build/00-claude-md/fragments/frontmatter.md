---
# about
name: fragment-frontmatter
type: fragment
project: ""
description: Padrão de frontmatter YAML — campos obrigatórios, valores aceitos e regras de uso para todos os recursos.
tags: [frontmatter, standard, metadata]

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

## Padrão de Frontmatter

Todo arquivo de recurso (skill, agent, hook, plugin, command, instruction, doc, fragment, readme) deve ter frontmatter YAML completo no topo do arquivo.

### Campos obrigatórios

```yaml
# about
name: resource-name           # nome em kebab-case
type: skill                   # tipo do recurso (ver valores aceitos abaixo)
project: ""                   # projeto onde está instalado
description: ""               # uma frase objetiva — usada pelo Claude para correspondência
tags: []                      # categorias em kebab-case

# history
author: ""
created: ""                   # YYYY-MM-DD
status: draft                 # ciclo de vida (ver valores aceitos abaixo)
version: 1.0.0                # semântico: major.minor.patch
updated: ""                   # YYYY-MM-DD — atualizado automaticamente pelo cli

# system
scope: project                # onde o recurso é instalado (ver valores aceitos abaixo)
source: ""                    # hub/<type>/<name>@<version> | local
auto_load: false              # carregar automaticamente na sessão ou apenas sob demanda
checksum: ""                  # SHA-256 do conteúdo — gerado automaticamente
dependencies: []              # recursos que precisam estar instalados antes deste
```

### Valores aceitos

**`type`**
`skill` | `agent` | `hook` | `plugin` | `command` | `instruction` | `doc` | `fragment` | `readme`

**`status`**
`draft` | `review` | `stable` | `deprecated`

**`scope`**
`global` — instalado em `~/.claude/`, disponível em todos os projetos
`project` — instalado em `.claude/`, disponível apenas neste repositório

### Campos gerados automaticamente pelo cli

Nunca preencher manualmente:

| Campo | Quando é gerado | Valor |
|---|---|---|
| `project` | No install | Nome do projeto destino |
| `source` | No install | `hub/<type>/<name>@<version>` ou `local` |
| `checksum` | No install e no publish | Hash SHA-256 do conteúdo do arquivo |
| `updated` | No install e no publish | Data da operação em `YYYY-MM-DD` |

### Regras de uso

- `auto_load: true` deve ser exceção — usar apenas para recursos invariavelmente necessários em toda sessão
- Recursos com `status: deprecated` não devem ser instalados em novos projetos
