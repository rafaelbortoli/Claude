---
# identity
name: Claude
type: doc
version: 1.0.0
status: stable

# context
description: Instruções específicas do projeto — estende ~/.claude/CLAUDE.md.
tags: []

# loading
scope: project
auto_load: true

# traceability — preenchidos pelo /setup-claude
source: build/00-claude-md/project.md
project: Claude
dependencies: []
checksum: ""

# metadata
author: ""
created: 2026-05-10
updated: 2026-05-10
---

# Claude — Instruções do Projeto

> Estende `~/.claude/CLAUDE.md`.
> Preencha as seções abaixo com o contexto específico deste repositório.

---

## Visão Geral

<!-- Uma frase descrevendo o que este projeto faz e seu objetivo principal -->

---

## Arquitetura

<!-- Descreva as camadas, módulos principais e como se relacionam.
     Exemplo:
     - `src/domain/` — entidades e regras de negócio, sem dependências externas
     - `src/app/` — casos de uso
     - `src/infra/` — gateways, banco de dados, serviços externos
     - `src/ui/` — componentes e páginas
-->

---

## Stack do Projeto

| Camada | Stack |
|---|---|
| Back-end | <!-- ex: Supabase + Edge Functions --> |
| Front-end | <!-- ex: Next.js + Tailwind --> |
| AI | <!-- ex: Claude SDK --> |
| Orquestração | <!-- ex: a definir --> |

---

## Convenções

<!-- Regras específicas deste projeto que sobrepõem o global.
     Exemplo:
     - Componentes React em PascalCase dentro de `src/ui/components/`
     - Nunca importar de `infra` dentro de `domain`
     - Migrations sempre revisadas antes de aplicar
-->

---

## Mapa do Repositório

<!-- Onde as coisas vivem e por quê.
     Exemplo:
     - `docs/` — documentação técnica e decisões de arquitetura
     - `supabase/migrations/` — migrations versionadas
     - `src/` — código da aplicação
     - `.claude/` — configuração do Claude para este projeto
-->

---

## Recursos Instalados

<!-- Atualizado automaticamente pelo install-resource.
     Exemplo:
     | Recurso | Tipo | Versão | Instalado em |
     |---|---|---|---|
     | `/skill-name` | skill | 1.0.0 | 2026-05-10 |
-->

---

## Restrições

<!-- Ações que exigem atenção especial neste projeto.
     Exemplo:
     - Nunca alterar schema do banco sem migration versionada
     - Não commitar variáveis de ambiente
     - PRs para `main` exigem revisão manual
-->
