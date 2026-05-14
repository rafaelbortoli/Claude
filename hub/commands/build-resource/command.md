---
# about
id: cmd-004
name: build-resource
type: command
project: ""
description: Cria um novo recurso no projeto atual a partir do template correspondente.
tags: [build, resource, template]

# history
author: ""
created: 2026-05-10
status: stable
version: 1.4.0
updated: 2026-05-14

# system
scope: global
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# /build-resource

Cria um novo recurso no projeto a partir do template correspondente.

Compatível com: `skill`, `agent`, `hook`, `command`, `plugin`.

---

## Passo 1 — Caminho do projeto

Execute:

```bash
pwd
```

**[smart-suggestions: on]** Sugestões de caminho baseadas no diretório atual e pastas irmãs.

Antes de perguntar:
1. Use o caminho retornado por `pwd` como primeira opção
2. Liste as pastas no diretório pai com `ls <diretório-pai>` e identifique até 2 pastas irmãs relevantes (que pareçam projetos: contêm `.claude/`, `package.json`, `pyproject.toml` ou similar)

Se houver pastas irmãs relevantes: use `AskUserQuestion` com até 3 caminhos e **"Outro caminho (digitar)"** como quarta opção.
Se não houver: use `AskUserQuestion` com apenas 2 opções:
- **"Sim, usar `<caminho retornado>`"**
- **"Não, informar outro caminho"**

Se o usuário escolher "Outro": pergunte em texto livre e aguarde a resposta.

Guarde o caminho escolhido como `<projeto>`.

## Passo 2 — Tipo do recurso

São 5 opções — exiba como lista e peça ao usuário que informe o tipo:

- `skill` — skill instalada em `.claude/skills/`
- `agent` — agente instalado em `.claude/agents/`
- `hook` — hook de evento instalado em `.claude/hooks/`
- `command` — comando instalado em `.claude/commands/`
- `plugin` — plugin com múltiplos recursos

## Passo 3 — Nome do recurso

**[smart-suggestions: on]** Sugestões de nome baseadas nos recursos já instalados.

Antes de perguntar:
1. Liste os recursos instalados: `ls <projeto>/.claude/skills/ <projeto>/.claude/agents/ <projeto>/.claude/commands/` (ignore erros se a pasta não existir)
2. Identifique o padrão de nomenclatura dos arquivos existentes (ex: `ux-writing-review`, `code-review` → padrão `<domínio>-<ação>`)
3. Com base no tipo escolhido no Passo 2, gere até 3 sugestões de nome que seguem o mesmo padrão

Se houver pelo menos 1 sugestão: use `AskUserQuestion` com as sugestões e **"Outro (digitar)"** como quarta opção.
Se não houver recursos instalados ou padrão identificável: pergunte em texto livre: _"Qual o nome do recurso? (ex: ux-writing-review)"_

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

Guarde como `<nome>`.

## Execução

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli build-resource --type "<tipo>" --name "<nome>" --dest "<projeto>/.claude"
```

---

## Pós-execução — Preenchimento assistido

Mostre o arquivo criado ao usuário.

Leia o frontmatter do arquivo criado. Se `description` estiver vazio ou com placeholder, prossiga com o preenchimento assistido abaixo. Caso contrário, oriente o usuário a revisar os campos antes de usar `/publish-resource`.

### Description

**[smart-suggestions: on]** Sugestões de descrição baseadas no conteúdo do arquivo.

1. Leia o corpo do arquivo criado (seções "O que faz", "Quando usar", "Instruções" ou equivalentes)
2. Gere 3 variações de descrição em uma frase, objetivas e no mesmo estilo das já existentes nos outros recursos
3. Use `AskUserQuestion` com as 3 variações e **"Outro (digitar)"** como quarta opção

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.

### Tags

**[smart-suggestions: on]** Sugestões de tags baseadas no CLAUDE.md e nos recursos existentes.

1. Leia `<projeto>/.claude/CLAUDE.md` — extraia os campos: `domain`, `project_type`, `audience`, `keywords`
2. Leia as tags já usadas em outros recursos do projeto (`.claude/skills/*.md`, `.claude/agents/*.md`)
3. Monte até 3 conjuntos de tags relevantes, agrupados por categoria:
   - Domínio: derivado de `domain` (ex: `fintech`)
   - Função: derivado do conteúdo do recurso (ex: `review`, `validation`)
   - Audiência: derivado de `audience` (ex: `b2b`)
4. Use `AskUserQuestion` com `multiSelect: true`, exibindo cada conjunto como uma opção (ex: `fintech, review, b2b`), e **"Outro (digitar)"** como quarta opção

Se o usuário escolher "Outro (digitar)": pergunte em texto livre e aguarde a resposta.
Se não houver campos preenchidos no CLAUDE.md: pergunte em texto livre: _"Quais tags identificam este recurso? (ex: review, ux, interface)"_

Após coletar description e tags, escreva os valores no frontmatter do arquivo criado e mostre o resultado final.
