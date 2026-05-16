# Plano — smart-suggestions

## Contexto

Os comandos do hub (build-resource, publish-resource, setup-claude) fazem perguntas em texto livre ou com opções fixas. O usuário precisa saber de antemão o que responder — nomes de recursos, descrições, tags — sem nenhuma orientação baseada no contexto do projeto.

A feature `smart-suggestions` introduz um padrão de perguntas inteligentes: Claude analisa o contexto disponível (CLAUDE.md, estrutura do projeto, arquivo sendo processado) e gera opções relevantes antes de perguntar. Cada pergunta pode habilitar ou desabilitar esse comportamento individualmente.

---

## Conceito — o toggle

Cada pergunta em um `command.md` pode declarar se usa smart-suggestions com uma anotação inline:

```markdown
**[smart-suggestions: on]** Pergunte o nome do recurso.
```

```markdown
**[smart-suggestions: off]** Pergunte o tipo do recurso.
```

Quando `on`: Claude lê o contexto, gera até 3 opções e apresenta via `AskUserQuestion`, com uma quarta opção "Outro (digitar)".

Quando `off` (ou ausente): pergunta direta em texto livre, sem geração de sugestões.

O toggle é por pergunta — não é global. Uma pergunta complexa pode ter `on` enquanto uma pergunta simples mantém `off`.

### Exemplo em command.md

```markdown
## Passo 3 — Nome do recurso

**[smart-suggestions: on]** Pergunte o nome do recurso.

Antes de perguntar:
1. Leia os recursos existentes em `.claude/skills/`, `.claude/agents/`, `.claude/commands/`
2. Identifique o padrão de nomenclatura (ex: `ux-writing-review` → padrão `<domínio>-<ação>`)
3. Gere até 3 sugestões que seguem o mesmo padrão, baseadas no tipo sendo criado

Use `AskUserQuestion` com as sugestões como opções e "Outro (digitar)" como quarta opção.
```

### Fluxo após "Outro (digitar)"

Quando o usuário seleciona "Outro (digitar)", Claude faz a pergunta original em texto livre no chat e aguarda a resposta antes de prosseguir. Não há nova pergunta via `AskUserQuestion`.

---

## Fontes de contexto

Claude usa as seguintes fontes para gerar sugestões, em ordem de prioridade:

| Fonte | Usado para |
|---|---|
| `CLAUDE.md` — campos de identidade (name, description, tags) | Nome do projeto, descrição, tags base |
| `CLAUDE.md` — novos campos (domínio, tipo, público, estágio, palavras-chave) | Tags de domínio, sugestões de descrição calibradas |
| Arquivo sendo processado (frontmatter + corpo) | Descrição e tags do recurso específico |
| Recursos já instalados no projeto (`.claude/skills/`, `.claude/agents/`) | Convenções de nomenclatura |
| Estrutura de pastas do projeto (`ls`, `pwd`) | Sugestão de caminhos |

### Fallback quando novos campos não estão preenchidos

As sugestões degradam graciosamente quando os campos da Fase 1 estão ausentes:

| Campo ausente | Comportamento |
|---|---|
| `domain` | Tags de domínio omitidas; demais sugestões mantidas |
| `project_type` | Categoria omitida das sugestões |
| `audience` | Tags de audiência omitidas |
| `stage` | Sem impacto nas sugestões de nome/descrição |
| `keywords` | Seeds de tags reduzidos ao conteúdo do arquivo |
| Todos ausentes | Sugestões baseadas apenas no arquivo e recursos instalados |

Nunca exibir `AskUserQuestion` com opções vazias. Se não houver sugestões suficientes (mínimo 1), fazer a pergunta em texto livre sem `AskUserQuestion`.

---

## Novos campos no CLAUDE.md

Para habilitar sugestões mais assertivas de descrição e tags, o `/setup-claude` deve coletar 5 campos adicionais na configuração inicial:

| Campo | Valores de exemplo | Usado para |
|---|---|---|
| `domain` | fintech, edtech, healthtech, e-commerce, saas-horizontal | Tags de domínio automáticas |
| `project_type` | saas, marketplace, api, cli, app-interno, ferramenta | Categoria principal do projeto e dos recursos |
| `audience` | b2b, b2c, developers, equipe-interna | Tom das descrições, tags de audiência |
| `stage` | mvp, beta, producao | Evita publicar recursos `draft` sem querer; calibra sugestões |
| `keywords` | lista de 2-4 termos que definem o produto | Seeds para geração de tags e descrições |

Esses campos devem ser adicionados à seção `# system` do frontmatter do `CLAUDE.md`:

```yaml
# system
domain: fintech
project_type: saas
audience: b2b
stage: mvp
keywords: [pagamentos, recorrência, split, marketplace]
```

---

## Comportamento por tipo de pergunta

### Caminho do projeto
**Contexto usado:** `pwd`, pastas irmãs no mesmo nível

**Sugestões geradas:**
1. Caminho atual (retornado por `pwd`)
2. Até 2 pastas irmãs relevantes encontradas no mesmo diretório pai
3. "Outro caminho" (texto livre)

---

### Nome do recurso
**Contexto usado:** recursos já instalados (`.claude/skills/`, `.claude/agents/`, `.claude/commands/`)

**Sugestões geradas:** Claude identifica o padrão de nomenclatura dos recursos existentes (ex: `ux-writing-review`, `code-review` → padrão `<ação>-<objeto>`) e sugere nomes que seguem a mesma convenção, baseados no tipo de recurso sendo criado.

---

### Descrição do recurso
**Contexto usado:** frontmatter + corpo do arquivo sendo processado; `CLAUDE.md` (domain, project_type, keywords)

**Sugestões geradas:** 3 variações de descrição geradas a partir do conteúdo do arquivo (seções "O que faz", "Quando usar", "Instruções"), calibradas pelo domínio e tipo do projeto. Quarta opção: "Outro (digitar)".

---

### Tags do recurso
**Contexto usado:** `CLAUDE.md` (domain, project_type, audience, keywords); tags já usadas em outros recursos do projeto

**Sugestões geradas:** conjuntos de tags relevantes agrupados por categoria. Claude apresenta até 3 conjuntos como opções no `AskUserQuestion` (multiSelect: true).

Exemplo de como as opções aparecem:

```
Opção 1: fintech, review, nextjs, b2b
Opção 2: fintech, validation, supabase, b2b
Opção 3: pagamentos, review, typescript
Outro (digitar)
```

O usuário pode selecionar um ou mais conjuntos. Claude combina as tags selecionadas (sem duplicatas) como valor final do campo.

---

### Confirmações (Sim/Cancelar)
Sempre usam `AskUserQuestion` com opções fixas. Smart-suggestions não se aplica — não há contexto a gerar.

---

## Escopo de implementação

### Fase 1 — Fundação (setup-claude)
- Adicionar os 5 novos campos ao fluxo de `/setup-claude` como perguntas interativas
- Atualizar o template de `CLAUDE.md` com os novos campos na seção `# system`
- Documentar os valores aceitos para cada campo

### Fase 2 — build-resource
- Habilitar smart-suggestions para: caminho do projeto, nome do recurso
- Após criação do arquivo: habilitar smart-suggestions para description e tags (preencher antes de encerrar)

### Fase 3 — publish-resource
- Habilitar smart-suggestions para: description e tags (quando ausentes ou vazios, antes de `--validate-only`)

### Fase 4 — Padrão para novos comandos
- Criar `hub/instructions/smart-suggestions-guide.md` documentando a convenção `[smart-suggestions: on/off]`
- Checklist para novos `command.md`: quais perguntas devem ter `on` por padrão

---

## Decisões de design

| Decisão | Justificativa |
|---|---|
| Toggle por pergunta, não global | Algumas perguntas não têm contexto suficiente para sugestões úteis. Forçar sugestões vazias é pior que texto livre. |
| Máximo 3 sugestões + "Outro" | Limite do `AskUserQuestion` (4 opções). A quarta sempre reservada para entrada livre. |
| Claude gera as sugestões (não CLI) | Operação semântica — requer leitura e interpretação de contexto. CLI é determinístico. |
| Novos campos em `# system` do CLAUDE.md | Campos de identidade do projeto pertencem ao frontmatter. Leitura automática por qualquer comando. |
| Sugestões são opções, não respostas | O usuário sempre pode recusar todas e digitar livremente. Smart-suggestions orienta, não limita. |
| Fallback para texto livre sem erro | Projetos sem CLAUDE.md preenchido não devem falhar — degradam para comportamento padrão. |
| Tags apresentadas como conjuntos | Tags individuais no AskUserQuestion exigiriam múltiplas rodadas. Conjuntos permitem seleção rápida e combinação via multiSelect. |

---

## Verificação

1. `/setup-claude` em novo projeto → confirmar que coleta os 5 novos campos e grava no CLAUDE.md
2. `/build-resource` skill → confirmar sugestões de nome baseadas em recursos existentes
3. `/build-resource` skill → confirmar sugestões de description e tags após criação
4. `/publish-resource` com description vazia → confirmar sugestões geradas antes de validate-only
5. Projeto sem CLAUDE.md preenchido → confirmar fallback para texto livre sem erro
6. Selecionar "Outro (digitar)" → confirmar que Claude pergunta em texto livre no chat
