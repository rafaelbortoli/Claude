---
feature: publish-resource
status: done
created: 2026-05-14
---

# Tasks — publish-resource

## CLI — Python

- [x] **T1** Adicionar validação de `CLAUDE.md` em `publish_resource.py`
  - Após resolver `src_dir`, verificar se `(src_dir / "CLAUDE.md").exists()`
  - Raise `FileNotFoundError` com mensagem clara se ausente
  - Arquivo: `cli/commands/publish_resource.py`

- [x] **T2** Adicionar flag `--validate-only` em `publish_resource.py`
  - Executa validação de `CLAUDE.md` e campos obrigatórios e encerra sem publicar
  - Usado pelo `command.md` antes de entrar no fluxo de seleção
  - Arquivo: `cli/commands/publish_resource.py`

- [x] **T3** Remover confirmação interativa do CLI em `publish_resource.py`
  - Remover qualquer `input()` de confirmação — Claude trata confirmação no `command.md`
  - Manter `_show_diff()` como informativo (sem prompt)
  - Arquivo: `cli/commands/publish_resource.py`
  - Nota: `input()` nunca estava presente; `_show_diff()` já era informativo

- [x] **T4** Atualizar `source` no arquivo local após publicação em `publish_resource.py`
  - Após publicar com sucesso, gravar `source: hub/<tipo>s/<nome>@<versão>` no arquivo local
  - Usar `frontmatter.write(src, {"version": version, "source": f"hub/{resource_type}s/{name}@{version}"})`
  - Aplicar também em `_publish_hook()` para hooks
  - Arquivo: `cli/commands/publish_resource.py`

- [x] **T5** Adicionar validação de `CLAUDE.md` em `build_resource.py`
  - Após resolver `dest_dir`, verificar se `(dest_dir / "CLAUDE.md").exists()`
  - Raise `FileNotFoundError` com mensagem clara se ausente
  - Arquivo: `cli/commands/build_resource.py`

## command.md — Fluxo

- [x] **T6** Reescrever `hub/commands/build-resource/command.md`
  - Passo 1: resolver caminho do projeto (`pwd` → perguntar se diferente)
  - Passo 2: perguntar nome do recurso
  - Passo 3: perguntar tipo
  - Executar com `--dest "<projeto>/.claude"`
  - Arquivo: `hub/commands/build-resource/command.md`

- [x] **T7** Reescrever `hub/commands/publish-resource/command.md`
  - Passo 1: resolver caminho do projeto
  - Passo 2: perguntar tipo (`skill`, `agent`, `command`)
  - Passo 3: listar recursos instalados do tipo via `list-resources --installed`
  - Passo 4: selecionar recurso pelo ID
  - Passo 5: executar `--validate-only` e exibir erros se houver
  - Passo 6: ler `source` do frontmatter e determinar cenário (novo vs existente)
  - **Cenário A** (source: local): apresentar conteúdo, confirmar, escrever arquivo limpo, publicar
  - **Cenário B** (source: hub/...): aviso de impacto, confirmar, comparar versões, listar mudanças, seleção, revisão do pacote, confirmar, escrever arquivo mesclado, publicar
  - Arquivo: `hub/commands/publish-resource/command.md`

## Sincronização

- [x] **T8** Sincronizar `~/.claude/commands/build-resource.md` com o hub
  - Copiar `hub/commands/build-resource/command.md` → `~/.claude/commands/build-resource.md`

- [x] **T9** Sincronizar `~/.claude/commands/publish-resource.md` com o hub
  - Copiar `hub/commands/publish-resource/command.md` → `~/.claude/commands/publish-resource.md`

## Registry

- [x] **T10** Atualizar `registry.json` com novas versões
  - `build-resource`: 1.2.0 → 1.3.0
  - `publish-resource`: 1.2.0 → 1.3.0
  - Arquivo: `registry.json`
