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

Use `AskUserQuestion`:
- **"Sim, usar `<caminho retornado>`"** — confirma o diretório atual como projeto
- **"Não, informar outro caminho"** — solicita o caminho correto em texto livre

Se o usuário escolher "Não", peça o caminho e guarde como `<projeto>`. Caso contrário, use o caminho retornado pelo `pwd`.

### Passo 2 — Tipo do recurso

Use `AskUserQuestion`:
- **"skill"** — recursos em `.claude/skills/`
- **"agent"** — recursos em `.claude/agents/`
- **"command"** — recursos em `.claude/commands/` (excluindo proxies)

### Passo 3 — Listar recursos disponíveis

Execute:

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli list-resources --installed --type "<tipo>" --dest "<projeto>/.claude"
```

Se a lista estiver vazia, informe e encerre.

### Passo 4 — Selecionar o recurso

Se a lista retornada tiver **até 4 itens**: use `AskUserQuestion` com cada recurso como opção (exibir nome e descrição).

Se tiver **mais de 4 itens**: exiba a tabela retornada pelo CLI e peça ao usuário que informe o ID ou nome do recurso.

Resolva o nome do recurso a partir da lista. Guarde como `<nome>`.

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

**Passo A3** — Use `AskUserQuestion`:
- **"Confirmar e publicar"** — prossegue para escrita e publicação
- **"Cancelar"** — encerra sem publicar

**Passo A4** — Escreva o arquivo local com o conteúdo limpo:
- Remova `project` e `source` do frontmatter
- Remova paths absolutos e referências ao projeto do corpo
- **Não altere `version`** — o bump é responsabilidade do CLI

→ Avance para a Fase 4.

---

### Cenário B — Recurso instalado do hub (`source: hub/...`)

O recurso foi instalado do hub e modificado localmente.

**Passo B1** — Exiba exatamente esta mensagem, substituindo `<nome>` e `<tipo>` pelos valores reais:

> **`<nome>`** já existe no hub e será atualizado.
> A seguir você verá as mudanças em relação à versão atual do hub e o conteúdo original, para escolher o que deve ser incluído na atualização.

Prossiga imediatamente para o Passo B2.

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

**Passo B4** — Para cada seção com diferenças, exiba uma comparação lado a lado no estilo diff de código:
- Coluna esquerda: conteúdo atual do hub (prefixo `−`)
- Coluna direita: conteúdo local modificado (prefixo `+`)
- Linhas iguais: exibir sem prefixo como contexto

Exemplo de formato:

```diff
## Instruções

− 1. Ler os arquivos indicados
− 2. Verificar critério A
+ 1. Ler os arquivos indicados
+ 2. Verificar critério A
+ 3. Verificar critério B (novo)
```

Se não houver mudanças relevantes após excluir informações de projeto, informe e encerre.

**Passo B5** — Apresente as seções alteradas para seleção:

Se houver **até 4 seções alteradas**: use `AskUserQuestion` com `multiSelect: true`, listando cada seção como opção.

Se houver **mais de 4 seções alteradas**: exiba a lista numerada das seções e peça ao usuário que informe quais deseja incluir.

Se nenhuma for selecionada, encerre.

**Passo B6** — Apresente o pacote final para revisão:

**As informações do projeto não serão enviadas para o hub.** Liste os campos e conteúdos que serão removidos antes da publicação:
- Campos do frontmatter: `project`, `source` (e quaisquer outros específicos do projeto)
- Paths absolutos ou referências ao projeto encontrados no corpo (listar cada ocorrência)

Em seguida exiba o **conteúdo final** que será publicado: versão do hub com as mudanças selecionadas aplicadas.

Use `AskUserQuestion`:
- **"Confirmar e publicar"** — prossegue para escrita e publicação
- **"Cancelar"** — encerra sem publicar

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
