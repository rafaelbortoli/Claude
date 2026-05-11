---
name: setup-claude
type: command
version: 1.3.0
status: stable

description: Configura a estrutura .claude/ em um novo projeto — cria diretórios, CLAUDE.md e estrutura de pastas do projeto.
tags: [setup, project, init]

scope: global
auto_load: false

source: hub/commands/setup-claude@1.3.0
project: Claude
dependencies: []
checksum: ""

author: ""
created: 2026-05-11
updated: 2026-05-10
---

# /setup-claude

> **Instruções de execução — siga esta sequência:**
>
> 1. Verifique se `~/.claude/hub-path` existe:
>    ```bash
>    cat ~/.claude/hub-path
>    ```
>    Se não existir, peça ao usuário para executar `/claude-start` primeiro.
>
> 2. Pergunte o nome da pasta do projeto (não assuma que é o mesmo que o nome do projeto):
>    "Qual é a pasta do projeto? (ex: ~/Code/MeuProjeto)"
>
> 3. Pergunte o nome do projeto:
>    "Qual o nome do projeto?"
>
> 4. Confirme com o usuário antes de executar:
>    "Vou configurar o projeto **<nome>** em `<pasta>`. Confirma?"
>
> 5. Execute:
>    ```bash
>    HUB_DIR="$(cat ~/.claude/hub-path)"
>    cd <pasta> && bash "$HUB_DIR/install.sh" setup-claude <nome>
>    ```
>
> 6. **Fluxo guiado de preenchimento do CLAUDE.md** — percorra cada seção abaixo em ordem,
>    nunca assuma o conteúdo, sempre apresente as opções disponíveis e aguarde a resposta
>    do usuário antes de passar para a próxima seção. Após coletar todas as respostas,
>    edite o arquivo `<pasta>/.claude/CLAUDE.md` substituindo os blocos de comentário
>    pelo conteúdo escolhido.
>
>    **Seção: Visão Geral**
>    Pergunta aberta — sem opção padrão:
>    "Visão Geral: descreva em uma frase o que este projeto faz e seu objetivo principal."
>
>    **Seção: Arquitetura**
>    Preencher automaticamente com base na estrutura de pastas criada pelo bootstrap:
>    ```
>    - `design/` — assets de marca e design do produto
>    - `dev/00-vision/` — briefing, escopo e requisitos
>    - `dev/01-architecture/` — diagramas e decisões técnicas
>    - `dev/02-supabase/` — migrations, schemas e Edge Functions
>    - `dev/03-app/` — rotas e páginas (Next.js App Router)
>    - `dev/04-lib/` — funções utilitárias e código compartilhado
>    - `dev/05-hooks/` — React hooks customizados
>    - `dev/06-components/` — componentes reutilizáveis (ui/, layout/)
>    - `dev/07-types/` — definições de tipos TypeScript
>    - `dev/08-public/` — assets estáticos
>    ```
>    Não perguntar ao usuário — aplicar diretamente.
>
>    **Seção: Stack do Projeto**
>    Preencher automaticamente com a tabela padrão:
>    | Camada | Stack |
>    |---|---|
>    | Back-end | Supabase + Edge Functions |
>    | Front-end | Next.js + Tailwind |
>    | Deploy | Vercel |
>    | AI | Claude Agents SDK |
>    Não perguntar ao usuário — aplicar diretamente.
>
>    **Seção: Convenções**
>    Preencher automaticamente com o conjunto padrão:
>    **Código**
>    - Componentes em PascalCase
>    - Rotas em kebab-case
>    - Variáveis de ambiente nunca commitadas
>    - Migrations sempre revisadas antes de aplicar
>    **Marca**
>    - Todos os assets de marca originados de `design/01-branding/create/` (tokens de design, expressão visual, expressão verbal, direção criativa)
>    - Estratégia e diretrizes consultadas a partir de `design/01-branding/plan/`
>    - Tokens de design definidos em `design/01-branding/create/` antes de implementar no código
>    **Design**
>    - Wireframes e protótipos em `design/02-product/ux-ui/` antes de desenvolver interfaces
>    Não perguntar ao usuário — aplicar diretamente.
>
>    **Seção: Mapa do Repositório**
>    Preencher automaticamente com base na estrutura criada pelo bootstrap:
>    ```
>    - `.claude/` — configuração do Claude para este projeto
>    - `design/01-branding/` — identidade de marca (research/, plan/, create/)
>    - `design/02-product/` — design do produto (discovery/, ux-ui/)
>    - `dev/00-vision/` — briefing, escopo e requisitos
>    - `dev/01-architecture/` — diagramas e decisões técnicas
>    - `dev/02-supabase/` — migrations, schemas e Edge Functions
>    - `dev/03-app/` — rotas e páginas (Next.js App Router)
>    - `dev/04-lib/` — funções utilitárias e código compartilhado
>    - `dev/05-hooks/` — React hooks customizados
>    - `dev/06-components/` — componentes reutilizáveis (ui/, layout/)
>    - `dev/07-types/` — definições de tipos TypeScript
>    - `dev/08-public/` — assets estáticos
>    ```
>    Não perguntar ao usuário — aplicar diretamente.
>
>    **Seção: Restrições**
>    Preencher automaticamente com o conjunto padrão:
>    **Banco de dados**
>    - Nunca alterar schema sem migration versionada em `dev/02-supabase/`
>    - Migrations sempre revisadas antes de aplicar
>    **Segurança**
>    - Nunca commitar variáveis de ambiente (`.env*` sempre no `.gitignore`)
>    - Chaves de API nunca hardcoded no código
>    - Nunca logar, expor ou commitar dados sensíveis de usuários
>    **Git**
>    - PRs para `main` exigem revisão manual
>    - Nunca fazer force push em `main`
>    **Serviços externos**
>    - Nunca executar ações em Supabase ou Vercel sem confirmação explícita do usuário
>    **Marca**
>    - Nunca usar assets fora de `design/01-branding/create/` como fonte
>    - Nunca alterar tokens de design diretamente no código — alterar na fonte e propagar
>    **Autonomia do Claude**
>    - Decisões arquiteturais (novas dependências, mudança de estrutura, novas abstrações) exigem aprovação prévia
>    - Ações que afetam mais de 5 arquivos exigem apresentação de plano antes de executar
>    - Nunca expandir escopo além do que foi solicitado sem aprovação explícita
>    Não perguntar ao usuário — aplicar diretamente.
>
> 7. Após preencher todas as seções, faça a limpeza final do CLAUDE.md:
>    - Remova o bloco de cabeçalho instrutivo (`> Estende ~/.claude/CLAUDE.md...`) — cumpriu seu papel
>    - Atualize `description` no frontmatter com a Visão Geral fornecida pelo usuário
>    - `tags` e `stack` já foram gravados automaticamente pelo install.sh — não alterar
>
> 8. Confirme ao usuário que o CLAUDE.md foi preenchido e mostre o resultado final.

---

## Referência

Inicializa a estrutura `.claude/` em um novo projeto e cria a estrutura de pastas padrão. Executar uma vez por repositório — pode ser re-executado com segurança (idempotente).

Cria `.claude/` com a estrutura mínima:

```
.claude/
├── CLAUDE.md       ← instruções do projeto com frontmatter de identidade
├── settings.json   ← base de permissões
├── commands/       ← vazio
├── skills/         ← vazio
├── agents/         ← vazio
├── hooks/          ← vazio
└── plugins/        ← vazio
```

E a estrutura de pastas do projeto:

```
design/
├── 01-branding/
│   ├── research/
│   ├── plan/
│   └── create/
└── 02-product/
    ├── discovery/
    └── ux-ui/

dev/
├── 00-vision/
├── 01-architecture/
├── 02-supabase/
├── 03-app/
├── 04-lib/
├── 05-hooks/
├── 06-components/
│   ├── ui/
│   └── layout/
├── 07-types/
└── 08-public/
```

### Stack padrão

| Camada | Stack |
|---|---|
| Back-end | Supabase + Edge Functions |
| Front-end | Next.js + Tailwind |
| Deploy | Vercel |
| AI | Claude Agents SDK |
