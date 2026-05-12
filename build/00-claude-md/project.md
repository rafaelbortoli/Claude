---
# about
name: project-name
type: doc
project: ""
description: (preencher)
tags: []

# history
author: ""
created: ""
status: stable
version: 1.0.0
updated: ""
stack: ""

# system
scope: project
source: build/00-claude-md/project.md
auto_load: true
checksum: ""
dependencies: []
---

# [NOME DO PROJETO] — Instruções do Projeto

---

## Visão Geral

(preencher)

---

## Arquitetura

- `design/` — assets de marca e design do produto
- `dev/00-vision/` — briefing, escopo e requisitos
- `dev/01-architecture/` — diagramas e decisões técnicas
- `dev/02-supabase/` — migrations, schemas e Edge Functions
- `dev/03-app/` — rotas e páginas (Next.js App Router)
- `dev/04-lib/` — funções utilitárias e código compartilhado
- `dev/05-hooks/` — React hooks customizados
- `dev/06-components/` — componentes reutilizáveis (ui/, layout/)
- `dev/07-types/` — definições de tipos TypeScript
- `dev/08-public/` — assets estáticos

---

## Stack do Projeto

| Camada | Stack |
|---|---|
| Back-end | Supabase + Edge Functions |
| Front-end | Next.js + Tailwind |
| Deploy | Vercel |
| AI | Claude Agents SDK |

---

## Convenções

**Código**
- Componentes em PascalCase
- Rotas em kebab-case
- Variáveis de ambiente nunca commitadas
- Migrations sempre revisadas antes de aplicar

**Marca**
- Todos os assets de marca originados de `design/01-branding/create/` (tokens de design, expressão visual, expressão verbal, direção criativa)
- Estratégia e diretrizes consultadas a partir de `design/01-branding/plan/`
- Tokens de design definidos em `design/01-branding/create/` antes de implementar no código

**Design**
- Wireframes e protótipos em `design/02-product/ux-ui/` antes de desenvolver interfaces

---

## Mapa do Repositório

- `.claude/` — configuração do Claude para este projeto
- `design/01-branding/` — identidade de marca (research/, plan/, create/)
- `design/02-product/` — design do produto (discovery/, ux-ui/)
- `dev/00-vision/` — briefing, escopo e requisitos
- `dev/01-architecture/` — diagramas e decisões técnicas
- `dev/02-supabase/` — migrations, schemas e Edge Functions
- `dev/03-app/` — rotas e páginas (Next.js App Router)
- `dev/04-lib/` — funções utilitárias e código compartilhado
- `dev/05-hooks/` — React hooks customizados
- `dev/06-components/` — componentes reutilizáveis (ui/, layout/)
- `dev/07-types/` — definições de tipos TypeScript
- `dev/08-public/` — assets estáticos

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

**Banco de dados**
- Nunca alterar schema sem migration versionada em `dev/02-supabase/`
- Migrations sempre revisadas antes de aplicar

**Segurança**
- Nunca commitar variáveis de ambiente (`.env*` sempre no `.gitignore`)
- Chaves de API nunca hardcoded no código
- Nunca logar, expor ou commitar dados sensíveis de usuários

**Git**
- PRs para `main` exigem revisão manual
- Nunca fazer force push em `main`

**Serviços externos**
- Nunca executar ações em Supabase ou Vercel sem confirmação explícita do usuário

**Marca**
- Nunca usar assets fora de `design/01-branding/create/` como fonte
- Nunca alterar tokens de design diretamente no código — alterar na fonte e propagar

**Autonomia do Claude**
- Decisões arquiteturais (novas dependências, mudança de estrutura, novas abstrações) exigem aprovação prévia
- Ações que afetam mais de 5 arquivos exigem apresentação de plano antes de executar
- Nunca expandir escopo além do que foi solicitado sem aprovação explícita
