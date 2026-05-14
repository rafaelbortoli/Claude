---
# about
id: cmd-005
name: publish-resource
type: command
project: ""
description: Normaliza e publica um recurso do projeto no hub para reutilização em outros projetos.
tags: [publish, resource, hub]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.3.0
updated: 2026-05-14

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /publish-resource

Normaliza e publica um recurso do projeto no hub para reutilização em outros projetos.

Compatível com: `skill`, `agent`, `command`.

---

## Fase 1 — Identificar o recurso

### Passo 1 — Caminho do projeto

Execute:

```bash
pwd
```

Mostre o caminho retornado e pergunte: _"Este é o diretório do projeto? Se não, informe o caminho correto."_

Guarde o caminho como `<projeto>`.

### Passo 2 — Tipo do recurso

Pergunte: _"Qual o tipo de recurso a publicar? Opções: `skill`, `agent`, `command`"_

### Passo 3 — Listar recursos disponíveis

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --installed --type "<tipo>" --dest "<projeto>/.claude"
```

Mostre a lista ao usuário.

- Para `skill` e `agent`: exibe os recursos em `.claude/skills/` e `.claude/agents/`
- Para `command`: exibe somente arquivos reais (proxies são excluídos automaticamente)

Se a lista estiver vazia, informe e encerre.

### Passo 4 — Selecionar o recurso

Pergunte: _"Qual recurso deseja publicar? Informe o ID ou nome."_

Resolva o nome do recurso a partir da tabela retornada. Guarde como `<nome>`.

---

## Fase 2 — Validação

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli publish-resource --type "<tipo>" --name "<nome>" --src "<projeto>/.claude" --validate-only
```

Se houver erros, exiba-os e encerre. Oriente o usuário a corrigir os campos obrigatórios antes de tentar novamente.

---

## Fase 3 — Seleção por cenário

Leia o campo `source` do frontmatter do arquivo do recurso selecionado:

- `skill` → `<projeto>/.claude/skills/<nome>.md`
- `agent` → `<projeto>/.claude/agents/<nome>.md`
- `command` → `<projeto>/.claude/commands/<nome>.md`

---

### Cenário A — Novo recurso (`source: local`)

O recurso foi criado neste projeto e ainda não foi publicado no hub.

**Passo A1** — Informe ao usuário que esta é uma primeira publicação. Nenhuma versão existe no hub para comparar.

**Passo A2** — Leia o arquivo local. Apresente o conteúdo completo que será publicado, **excluindo**:
- Campo `project` do frontmatter
- Campo `source` do frontmatter
- Paths absolutos e referências específicas ao projeto encontradas no corpo

**Passo A3** — Pergunte: _"Este é o conteúdo que será publicado no hub. Confirma?"_

Se o usuário não confirmar, encerre sem publicar.

**Passo A4** — Escreva o arquivo local com o conteúdo limpo:
- Remova `project` e `source` do frontmatter
- Remova paths absolutos e referências ao projeto do corpo
- **Não altere `version`** — o bump é responsabilidade do CLI

→ Avance para a Fase 4.

---

### Cenário B — Recurso instalado do hub (`source: hub/...`)

O recurso foi instalado do hub e modificado localmente. Publicar criará uma nova versão disponível para todos os projetos que usam este recurso.

**Passo B1** — Avise:

> _"Este recurso foi instalado do hub. Publicar irá criar uma nova versão disponível para todos os projetos."_

Pergunte: _"Confirma que deseja publicar esta atualização?"_

Se o usuário não confirmar, encerre.

**Passo B2** — Leia os dois arquivos:

1. O arquivo local (ignorando `project`, `source`, `version`, `updated`, `checksum` e paths absolutos)
2. A versão atual do hub — execute para obter o caminho:
   ```bash
   cat ~/.claude/hub-path
   ```
   Leia o arquivo em: `<hub>/hub/<tipo>s/<nome>/<tipo>.md`

**Passo B3** — Identifique as diferenças entre o arquivo local e a versão do hub, seção por seção:
- No frontmatter: compare cada campo (exceto `project`, `source`, `version`, `updated`, `checksum`)
- No corpo: compare cada seção separadamente

**Passo B4** — Apresente a lista de mudanças encontradas. Para cada mudança mostre:
- Qual seção foi alterada
- Resumo claro do que foi adicionado, removido ou modificado

Se não houver mudanças relevantes após excluir informações de projeto, informe e encerre.

**Passo B5** — Pergunte ao usuário quais mudanças deseja publicar. O usuário pode selecionar todas, algumas ou nenhuma. Se nenhuma for selecionada, encerre.

**Passo B6** — Apresente o pacote final para revisão:

1. **Informações descartadas**: campos e referências de projeto que serão removidos
2. **Conteúdo final**: versão do hub com as mudanças selecionadas aplicadas

Pergunte: _"Este é o pacote que será publicado no hub. Confirma?"_

Se o usuário não confirmar, encerre.

**Passo B7** — Escreva o arquivo local com o conteúdo mesclado:
- Base: versão atual do hub
- Aplicar: mudanças selecionadas pelo usuário
- Excluir: campos `project`, `source` e paths absolutos do projeto
- **Não altere `version`** — o bump é responsabilidade do CLI

→ Avance para a Fase 4.

---

## Fase 4 — Publicação

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli publish-resource --type "<tipo>" --name "<nome>" --src "<projeto>/.claude"
```

O CLI irá:
- Fazer bump de versão (se o recurso já existe no hub) ou atribuir novo ID (se novo)
- Aplicar limpeza de segurança: remover `project`, `source` e normalizar paths
- Exibir o diff informativo do que foi publicado
- Atualizar `registry.json` e `CHANGELOG.md`
- Atualizar o arquivo local com `version` e `source: hub/<tipo>s/<nome>@<versão>`

Mostre o output completo ao usuário e confirme que o recurso foi promovido ao hub.
