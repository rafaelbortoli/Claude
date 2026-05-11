# Proposta: Setup de Projetos e Ciclo de Recursos

**Status**: aprovado
**Criado**: 2026-05-10

---

## Visão geral

Todo projeto novo parte com configuração mínima — apenas identidade e estrutura base. Recursos são adicionados sob demanda. Recursos criados no projeto podem ser publicados no hub para reutilização em outros projetos.

```
AMBIENTE GLOBAL          NOVO PROJETO             CICLO DE RECURSOS
────────────────         ────────────             ─────────────────
~/.claude/CLAUDE.md      .claude/CLAUDE.md        hub → install → projeto
~/.claude/settings.json  .claude/settings.json    new → cria no projeto
                         .claude/commands/         publish → projeto → hub
                         .claude/skills/
                         .claude/agents/
                         .claude/hooks/
                         .claude/plugins/
```

---

## Camadas de entrada

O `install.sh` é a implementação. O usuário não interage com ele diretamente — acessa via comandos no Claude Code.

| Camada | O que é | Quem chama |
|---|---|---|
| `install.sh` | Script shell — executa as operações | Claude, via Bash |
| `/claude-start` | Comando no hub — setup global da máquina | Usuário, uma vez por máquina |
| `/setup-claude` | Comando no hub — setup de novo projeto | Usuário, uma vez por projeto |
| `/install-resource` | Comando no hub — instala recurso do hub | Usuário, sob demanda |
| `/build-resource` | Comando no hub — cria recurso novo | Usuário, sob demanda |
| `/publish-resource` | Comando no hub — publica recurso no hub | Usuário, sob demanda |

---

## Cenário 1: primeira vez em uma máquina nova

Executado uma única vez ao configurar o ambiente de desenvolvimento.

```
Usuário digita /claude-start no Claude Code
  ↓
Claude executa: install.sh claude-start
  ↓
global/CLAUDE.md     → ~/.claude/CLAUDE.md
global/settings.json → ~/.claude/settings.json
```

Resultado: todas as sessões do Claude Code nesta máquina herdam as instruções globais e as permissões base.

---

## Cenário 2: novo projeto

Executado ao iniciar um novo repositório git.

```
Usuário abre Claude Code no diretório do novo projeto
  ↓
Usuário digita /setup-claude
  ↓
Claude pergunta: nome do projeto e stack
  ↓
Claude executa: install.sh setup-claude <nome> --stack <stack>
  ↓
Projeto configurado — nenhum recurso instalado
```

### Estrutura criada

```
.claude/
├── CLAUDE.md       ← build/00-claude-md/project.md com frontmatter do projeto
├── settings.json   ← global/settings.json base
├── commands/       ← vazio (slash commands instalados sob demanda)
├── skills/         ← vazio (skills instaladas sob demanda)
├── agents/         ← vazio (agentes instalados sob demanda)
├── hooks/          ← vazio (scripts de hook instalados sob demanda)
└── plugins/        ← manifesto dos plugins instalados (não contém os recursos em si)
```

> `instructions` não gera pasta — fragmentos são colados diretamente no `CLAUDE.md` do projeto durante a instalação.

### Frontmatter de identificação

Todo arquivo gerado no setup recebe identificação do projeto:

```markdown
---
project: my-project-name
stack: nextjs
created: 2026-05-10
---
# my-project-name — Instruções do Projeto
```

---

## Cenário 3: instalar recurso do hub no projeto

Executado sob demanda quando o usuário precisa de uma skill, agent, hook ou plugin.

```
Usuário digita /install-resource skill code-review
  ↓
Claude executa: install.sh install-resource skill code-review
  ↓
hub/skills/code-review/skill.md → .claude/skills/code-review.md
  + frontmatter de projeto injetado
```

### Frontmatter injetado na instalação

```yaml
---
name: code-review
description: ...
project: my-project-name
created: 2026-05-10
source: hub/skills/code-review@1.0.0
---
```

### Instalação de plugin

Um plugin instala todos os seus recursos em sequência:

```
install.sh install-resource plugin code-quality
  ↓
Lê hub/plugins/code-quality/plugin.json
  ↓
Para cada skill  → install skill <nome>
Para cada agent  → install agent <nome>
Para cada hook   → copia hook.sh + edita settings.json (com diff e confirmação)
Para cada command → copia .md para .claude/commands/
```

### Instalação de hook

Hooks exigem configuração no `settings.json`. O script edita o arquivo automaticamente — exibe o diff antes de aplicar e aguarda confirmação:

```
install.sh install-resource hook audit-log
  ↓
Copia hook.sh → .claude/hooks/audit-log.sh
  ↓
Gera settings.json atualizado com a entrada do hook
  ↓
Exibe diff do que será alterado
Aguarda confirmação do usuário
  ↓
Aplica a alteração em .claude/settings.json
```

> `--dry-run` exibe o diff sem aplicar.

---

## Cenário 4: criar novo recurso para o projeto

Cria um recurso a partir do template correspondente, pré-preenchido com a identidade do projeto.

```
Usuário digita /build-resource skill my-skill
  ↓
Claude executa: install.sh build-resource skill my-skill
  ↓
build/01-skills/_template/ → .claude/skills/my-skill.md
  + frontmatter com project + created + source: local
```

Frontmatter de recurso criado localmente:

```yaml
---
name: my-skill
description: (preencher)
project: my-project-name
created: 2026-05-10
source: local
---
```

> O mesmo se aplica a agents (→ `.claude/agents/`), hooks (→ `.claude/hooks/`) e commands (→ `.claude/commands/`). Cada tipo tem seu destino próprio.

---

## Cenário 5: publicar recurso do projeto no hub

Normaliza o recurso — remove informações específicas do projeto — e copia para o hub.

```
Usuário digita /publish-resource skill my-skill
  ↓
Claude executa: install.sh publish-resource skill my-skill
  ↓
Lê .claude/skills/my-skill.md
  ↓
Remove: project, installed, source, paths absolutos, nomes hardcoded
Normaliza: description genérica, placeholders nos exemplos
Bump de versão se já existe no hub
  ↓
Exibe diff do que será normalizado
Aguarda confirmação do usuário
  ↓
hub/skills/my-skill/skill.md   ← recurso normalizado
hub/skills/my-skill/skill.json ← gerado ou atualizado
registry.json                  ← atualizado
```

### O que é normalizado no publish

| Campo / conteúdo | Antes (projeto) | Depois (hub) |
|---|---|---|
| `project` | `my-project-name` | removido |
| `installed` | `2026-05-10` | removido |
| `source` | `local` | removido |
| Paths absolutos | `/Users/rafael/projeto/...` | removido ou parametrizado |
| Nomes hardcoded | `my-project-name` | substituído por placeholder |

---

## Interface completa do install.sh

```bash
# Setup global (uma vez por máquina)
install.sh claude-start

# Novo projeto
install.sh setup-claude <project-name> [--stack <stack>]

# Instalar recurso do hub
install.sh install-resource skill  <name>
install.sh install-resource agent  <name>
install.sh install-resource hook   <name>
install.sh install-resource plugin <name>

# Criar novo recurso
install.sh build-resource skill  <name>
install.sh build-resource agent  <name>
install.sh build-resource hook   <name>
install.sh build-resource plugin <name>

# Publicar recurso no hub
install.sh publish-resource skill  <name>
install.sh publish-resource agent  <name>
install.sh publish-resource hook   <name>
install.sh publish-resource plugin <name>

# Flags
--global      # opera em ~/.claude/ em vez de .claude/
--dry-run     # mostra o que seria feito sem executar
--stack       # define stack para setup-claude
```

---

## Estrutura interna do script

```
install.sh
│
├── cmd_init()
├── cmd_init_project()
│
├── cmd_install()
├── cmd_new()
├── cmd_publish()
│
├── util_inject_frontmatter()    # adiciona project/created/source
├── util_strip_frontmatter()     # remove campos específicos de projeto
├── util_edit_settings_json()    # edita settings.json com diff e confirmação
├── util_copy_versioned()        # cópia com verificação de versão
└── util_update_registry()       # atualiza registry.json
```

---

## Ponto de extensão: AI Self Improvement

O `publish` é o momento natural para uma camada de revisão automática antes de um recurso entrar no hub:

```
publish
  ↓ normaliza
  ↓ (futuro) agente revisa qualidade e coerência com padrões do hub
  ↓ exibe sugestões de melhoria
  ↓ aguarda confirmação
  → hub/
```

Esse agente de revisão será desenvolvido como parte das rotinas de AI Self Improvement — fora do escopo desta proposta.

---

## Decisões de design

### Conflito de versão no install

Quando o recurso já está instalado, o script pergunta ao usuário:

```
Recurso 'code-review@1.2.0' já instalado (versão atual: 1.0.0).
  [s] sobrescrever   [p] pular   [c] cancelar
```

### Stacks disponíveis

Stacks iniciais em `build/stacks/`:

| Stack | Descrição |
|---|---|
| `nextjs-supabase` | Full-stack — Next.js + Tailwind + Supabase |
| `generic` | Sem stack definida — plugins universais |

Novas stacks adicionadas conforme recursos específicos forem criados.

### Validação no publish

Dois níveis:

| Nível | Campos | Comportamento |
|---|---|---|
| Bloqueante | `name`, `type`, `version`, `description` | Impede o publish até serem preenchidos |
| Aviso | `author`, `tags` | Exibe alerta, mas permite publicar |
