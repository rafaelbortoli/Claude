---
title: fix-architecture
type: plan
status: approved
created: 2026-05-16
updated: 2026-05-16
---

# Plano — Ajuste Arquitetural do ClaudeSystem

## Contexto

O ClaudeSystem é o **engine** — infraestrutura instalada em projetos para habilitar resources, definir regras e acelerar planejamento e execução. Não é um projeto em si.

O hub (`hub/`) é a fonte canônica de todos os resources. Fica centralizado no ClaudeSystem e nunca é copiado para projetos. Quando um projeto precisa instalar um resource, o engine busca no hub via `~/.claude/hub-path`.

O problema identificado: `.claude/commands/` dentro do ClaudeSystem contém cópias instaladas dos recursos canônicos do hub — tratando o engine como se fosse um projeto. Isso cria drift entre versões e contradiz o papel do ClaudeSystem.

---

## Decisões de arquitetura

- ClaudeSystem é o engine, não um projeto
- Comandos existem para ser usados em projetos, não no ClaudeSystem
- O hub em `hub/` é a única fonte canônica — sem cópias instaladas no engine
- `scope: global` para commands já está implementado via `claude-start`, que copia todos os commands de `hub/commands/` para `~/.claude/commands/` automaticamente
- Mecanismo de update: editar no hub → rodar `claude-start` → propaga para `~/.claude/commands/`
- Atualizações do engine não propagam para projetos existentes — apenas novos projetos recebem o engine atualizado

---

## Plano de execução

### Fase 1 — Remover `.claude/commands/` do ClaudeSystem

Todos os 6 arquivos têm cópias canônicas em `hub/commands/` e já estão instalados globalmente em `~/.claude/commands/`. Nenhum dado será perdido e nenhuma funcionalidade será quebrada.

| Arquivo | Canônico em |
|---|---|
| `build-resource.md` | `hub/commands/build-resource/command.md` |
| `claude-start.md` | `hub/commands/claude-start/command.md` |
| `install-resource.md` | `hub/commands/install-resource/command.md` |
| `new-project.md` | `hub/commands/new-project/command.md` |
| `publish-resource.md` | `hub/commands/publish-resource/command.md` |
| `test-publish.md` | removido do hub (draft sem conteúdo) |

Remover os 6 arquivos e o diretório `.claude/commands/`.

### Fase 2 — Atualizar `.claude/CLAUDE.md`

Documentar:

- ClaudeSystem é o engine — não é um projeto
- Comandos vivem exclusivamente em `hub/commands/` e são instalados globalmente via `claude-start`
- Workflow de desenvolvimento: editar em `hub/`, rodar `claude-start` para propagar para `~/.claude/commands/`, testar a partir de qualquer sessão
- Não executar comandos de projeto dentro do ClaudeSystem

### Fase 3 — Sincronizar `~/.claude/commands/` com o hub

Rodar `claude-start` para propagar as atualizações feitas nesta sessão — `build-resource` está em v1.4.0 globalmente e v1.5.0 no hub.

```bash
/Users/rafaelbortoli/Code/ClaudeSystem/.venv/bin/python -m cli claude-start
```

### Fase 4 — Limpeza adicional

`setup-claude` existe em `~/.claude/commands/setup-claude.md` mas não tem correspondente em `hub/commands/`. Verificar origem e decidir: adicionar ao hub ou remover globalmente.

---

## O que permanece em `.claude/`

| Arquivo | Motivo |
|---|---|
| `CLAUDE.md` | Configuração do engine |
| `settings.json` | Configuração do Claude Code |
| `settings.local.json` | Configuração local |
| `launch.json` | Configuração de launch |
| `project.log` | Log de sessão |

---

## Lacunas resolvidas

| Lacuna | Resolução |
|---|---|
| Bootstrap sem ponto de entrada | `claude-start` já instala todos os commands globalmente via `_install_commands()`. Não há exceção necessária. |
| `scope: global` não implementado | Já implementado para commands em `claude_start.py:64`. Skills e agents ficam para iniciativa futura. |
| Conteúdo do CLAUDE.md | Especificado na Fase 2 acima. |
| `test-publish` sem conteúdo | Endereçado na Fase 4 — verificar origem de `setup-claude` e revisar `test-publish`. |
