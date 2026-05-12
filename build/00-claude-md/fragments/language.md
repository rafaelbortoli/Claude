---
# about
name: fragment-language
type: fragment
project: ""
description: Regras de idioma e nomenclatura — pt-BR para documentação, inglês para código.
tags: [language, naming, conventions]

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

## Idioma e Nomenclatura

### Comunicação e Documentação

- Todo conteúdo de chat, documentação e markdown em **pt-BR**
- Acentuação obrigatória: `não` (nunca `nao`), `você` (nunca `voce`), `próximo` (nunca `proximo`)
- Termos técnicos, nomes de frameworks e metodologias permanecem em inglês

### Código

- Identificadores (variáveis, funções, classes, módulos) em **inglês**
- Comentários inline e docstrings em **pt-BR**
- Strings voltadas ao usuário final em **pt-BR**

### Nomenclatura de Arquivos e Diretórios

| Contexto | Padrão | Exemplo |
|---|---|---|
| Arquivos Python | snake_case | `agent_runner.py` |
| Diretórios | kebab-case | `claude-md/` |
| Arquivos Markdown | kebab-case | `global.md` |
| Arquivos de configuração | kebab-case | `plugin.json` |
| Scripts shell | kebab-case | `pre-tool-use.sh` |
