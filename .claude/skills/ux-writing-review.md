---
# about
name: ux-writing-review
type: skill
project: Claude
description: Revisa, melhora ou reescreve textos de interface aplicando princípios de UX Writing.
tags: [ux-writing, copy, review, interface]

# history
author: Rafael Bortoli
created: 2026-05-11
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: local
auto_load: false
checksum: ""
dependencies: []
---

# UX Writing Review

## O que faz

Revisa, melhora ou reescreve textos de interface (micro-copy, mensagens, labels, botões, erros, tooltips, empty states) aplicando princípios de UX Writing.

## Quando usar

- Quando o usuário pedir revisão, melhoria ou reescrita de textos de interface
- Quando mencionar: botões, labels, mensagens de erro, tooltips, empty states, descrições curtas, textos de UI
- Quando pedir para "revisar texto", "melhorar copy", "reescrever mensagem", "checar UX Writing"
- Quando o usuário colar um texto curto e pedir feedback, sugestões ou melhorias — mesmo sem mencionar UX Writing explicitamente

## Não usar quando

- O texto for longo (artigos, documentações extensas, emails formais)
- O pedido for sobre conteúdo estratégico ou estrutura de informação — não apenas forma

## Instruções

### 1. Perguntas obrigatórias antes de revisar

Faça as duas perguntas abaixo, uma de cada vez, antes de qualquer revisão:

1. "Esse texto é para **equipe interna** (documentação, processos, sistemas internos) ou para **usuário final** (produto digital — app, site, plataforma)?"
2. "Qual é o contexto desse texto? Onde ele aparece e qual ação o usuário está tentando realizar?"

### 2. Princípios — aplique os relevantes, não todos

1. **Clareza** — uma única interpretação possível
2. **Objetividade** — sem palavras desnecessárias
3. **Utilidade** — ajuda o usuário a agir ou entender
4. **Acessibilidade** — linguagem simples, sem jargão
5. **Humanidade** — próximo, sem ser informal
6. **Consistência** — mesmos termos para os mesmos conceitos
7. **Orientação à ação** — verbos no imperativo, próximo passo claro
8. **Adequação ao contexto** — tom e formato alinhados ao componente
9. **Voz ativa** — sujeito age
10. **Segunda pessoa** — prefira "você"
11. **Limites por componente** — botões: até 3 palavras; tooltips: até 2 linhas; erros: causa + solução em 1–2 frases
12. **Erros construtivos** — o que aconteceu + por quê + o que fazer; nunca culpe o usuário

### 3. Regras

- Melhore a forma, não o conteúdo — não altere o significado
- Tom: direto, neutro, profissional — sem entusiasmo artificial
- Não use: "simplesmente", "facilmente", "apenas", "incrível"
- Prefira frases afirmativas
- Se o texto estiver adequado, diga isso — não force melhorias
- Se precisar de mais contexto, pergunte antes de reescrever
- Múltiplos textos: revise cada um separadamente

## Output

**Usuário final**
Texto original → texto revisado → princípios aplicados (1 linha de justificativa cada).
Se houver 2 reescritas igualmente válidas, apresente as duas com a diferença entre elas.

**Equipe interna**
Texto original → texto revisado. Sem explicação de princípios. Nota curta só se necessário.

## Referências

- `.claude/CLAUDE.md` — convenções e restrições do projeto
