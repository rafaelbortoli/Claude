---
# about
id: sk-002
name: translate-pt-to-eng
type: skill
description: Traduz textos do português para o inglês considerando convenções culturais e linguísticas americanas.
tags: [tradução, localização, inglês, pt-br, copy, brand-voice, adaptação-cultural, eua, branding, b2c, conteúdo, review]

# history
author: Bortoli
created: 2026-05-15
status: draft
version: 1.0.0
updated: 2026-05-15

# system
scope: global
auto_load: false
checksum: ""
dependencies: []
---

# Translate PT → EN

## O que faz

Traduz textos do português para o inglês americano, produzindo versões fiéis à intenção, tom e estrutura do original — naturais para um falante nativo — com adaptação cultural ao mercado dos EUA.

## Quando usar

- Quando o usuário pedir para traduzir, "passar para o inglês" ou "versão em inglês"
- Quando mencionar: "traduz", "translate", "tradução", "translation", "PT → EN", "inglês americano"
- Quando o usuário colar um texto em português e esperar claramente uma versão em inglês
- Quando pedir para "adaptar", "localizar" ou "reescrever para audiência internacional"
- Quando o contexto implicar tradução — ex: usuário compartilha material de marca em português e pede versão para mercado americano

## Não usar quando

- O texto já estiver em inglês
- O pedido for de revisão ou melhoria de um texto já em inglês — usar `/ux-writing-review`
- A direção for EN → PT

## Instruções

### 1. Identificar o tipo de texto

Inferir pelo tom e conteúdo:

- **Marketing** — taglines, headlines, CTAs, copy de produto, anúncios, landing pages
- **Corporativo** — e-mails, comunicados, apresentações, relatórios
- **Técnico** — interfaces, documentação, manuais, labels

Se o tipo não for identificável, pergunte antes de traduzir.

### 2. Aplicar as regras por tipo

**Todos os tipos**
- Preservar intenção, tom, formalidade e estrutura
- Adaptar expressões idiomáticas, gírias e referências culturais ao equivalente funcional em inglês americano — nunca traduzir literalmente
- Variante fixa: **American English**

**Marketing**
- Priorizar impacto emocional e persuasivo sobre fidelidade literal
- Adaptar headlines e CTAs para soar naturais ao mercado americano
- Preferir verbos de ação diretos (ex: "Get started", "Discover", "Shop now")

**Corporativo**
- Usar registro profissional americano — mais direto que o português formal
- Adaptar convenções de polidez (PT: formas de tratamento; EN: objetividade)

**Técnico**
- Priorizar terminologia consolidada em inglês
- Localizar labels de interface (ex: "Salvar" → "Save")
- Preservar listas numeradas e formatação

### 3. Verificar ambiguidades

Se houver ambiguidade genuína que afete o significado (pronome ambíguo, termo intraduzível, referência cultural sem equivalente direto): perguntar antes de entregar.

## Output

Retornar apenas o texto traduzido. Preservar a estrutura do original (parágrafos, listas, markdown). Sem notas, sem alternativas, sem comentários — exceto nos casos de ambiguidade descritos acima.

## Referências

- `.claude/CLAUDE.md` — convenções e restrições do projeto
- `design/01-branding/03-create/` — tom de voz e expressão verbal da marca
