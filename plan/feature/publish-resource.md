# Plano — Promoção de recursos do projeto para o hub

## Contexto

O sistema já tem `publish_resource.py` funcionando com lógica básica, mas o fluxo está incompleto para os dois cenários de promoção:

- **Novo recurso** (`source: local`): criado no projeto, nunca publicado no hub
- **Recurso existente** (`source: hub/tipo/nome@versão`): instalado do hub, modificado localmente

Gaps atuais:
- `command.md` não pede caminho do projeto, não passa `--src`, não lista recursos antes de pedir o nome
- `build-resource` tem o mesmo problema com `--dest`
- Não há limpeza explícita de informações do projeto antes de publicar
- Não há seleção granular de quais mudanças publicar
- Não há apresentação do pacote final (o que foi descartado vs o que será publicado)
- O `source` do arquivo local não é atualizado após publicação
- O fluxo não distingue skill/agent (com proxy) de command (sem proxy)

---

## Tipos suportados

| Tipo | Conteúdo em | Proxy em commands/ | Publicado em |
|---|---|---|---|
| `skill` | `.claude/skills/<name>.md` | ✅ criado na instalação | `hub/skills/<name>/skill.md` |
| `agent` | `.claude/agents/<name>.md` | ✅ criado na instalação | `hub/agents/<name>/agent.md` |
| `command` | `.claude/commands/<name>.md` | ❌ é o próprio arquivo | `hub/commands/<name>/command.md` |

---

## Fluxo aprovado

### Fase 1 — command.md (Claude)

1. Resolver caminho do projeto (`pwd` → perguntar se diferente). Guardar como `<projeto>`.
2. Perguntar tipo: `skill`, `agent` ou `command`
3. Listar recursos instalados do tipo via CLI:
   ```bash
   HUB_DIR="$(cat ~/.claude/hub-path)"
   "$HUB_DIR/.venv/bin/python" -m cli list-resources --installed --type "<tipo>" --dest "<projeto>/.claude"
   ```
   - skill → lista de `.claude/skills/`
   - agent → lista de `.claude/agents/`
   - command → lista de `.claude/commands/` excluindo proxies (`<!-- proxy:...`)
4. Selecionar recurso pelo ID. Resolver nome a partir da tabela.

### Fase 2 — CLI (validação)

Executar:
```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli publish-resource --type "<tipo>" --name "<nome>" --src "<projeto>/.claude" --validate-only
```

5. Validar presença de `CLAUDE.md` em `<projeto>/.claude/`
6. Validar campos obrigatórios (`name`, `type`, `version`, `description`)

Se inválido, exibir erros e encerrar.

### Fase 3 — command.md (seleção por cenário)

**Determinar cenário**: ler campo `source` do frontmatter do recurso selecionado.

---

**Cenário A — Novo recurso (`source: local`)**

7. Claude informa que é uma primeira publicação (nenhuma versão no hub para comparar)
8. Claude lê o arquivo local, ignora campos `project`, `source` e paths absolutos
9. Claude apresenta o conteúdo completo que será publicado
10. Usuário confirma ou cancela
11. Claude escreve o arquivo local com o conteúdo limpo:
    - Remove campos `project` e `source` do frontmatter
    - Remove paths absolutos e referências específicas do projeto do corpo
    - **Não altera `version`** — bump é responsabilidade do CLI
12. → Fase 4

---

**Cenário B — Recurso existente (`source: hub/tipo/nome@versão`)**

7. Claude avisa: _"Este recurso foi instalado do hub. Publicar irá atualizar a versão para todos os projetos."_
8. Usuário confirma ou cancela
9. Claude lê:
   - Arquivo local (ignorando `project`, `source`, paths)
   - Versão atual do hub em `<hub>/hub/<tipo>s/<nome>/<tipo>.md`
10. Claude identifica diferenças por seção (ex: "O que faz", "Instruções", "Output")
11. Claude apresenta a lista de mudanças, excluindo alterações de campos de projeto
12. Usuário seleciona quais mudanças publicar (pode cancelar se nenhuma)
13. Claude apresenta o pacote final:
    - **Informações descartadas**: campos e refs de projeto removidos
    - **Conteúdo final**: versão do hub + mudanças selecionadas
14. Usuário confirma ou cancela
15. Claude escreve o arquivo local com o conteúdo mesclado:
    - Base: versão atual do hub
    - Aplicar: mudanças selecionadas pelo usuário
    - Excluir: campos `project`, `source` e paths absolutos
    - **Não altera `version`** — bump é responsabilidade do CLI
16. → Fase 4

---

### Fase 4 — CLI (publicação)

```bash
HUB_DIR="$(cat ~/.claude/hub-path)"
"$HUB_DIR/.venv/bin/python" -m cli publish-resource --type "<tipo>" --name "<nome>" --src "<projeto>/.claude"
```

17. Bump de versão (se recurso já existe no hub) ou atribuir novo ID (se novo)
18. CLI aplica limpeza de segurança: `frontmatter.strip(["project", "source"])` + `normalize_body()`
    — camada de proteção mesmo que Claude já tenha feito a limpeza
19. Exibir diff informativo entre hub atual e versão a publicar (sem confirmação — Claude já confirmou)
20. Copiar para `hub/<tipo>s/<nome>/<tipo>.md`
21. Atualizar `registry.json` e `CHANGELOG.md`
22. Atualizar arquivo local: `version` + `source: hub/<tipo>s/<nome>@<versão>`

---

## Decisões de design

| Decisão | Justificativa |
|---|---|
| Claude faz comparação e merge (não CLI) | Operação semântica — envolve entender seções e contexto. CLI é determinístico; isso não é. |
| Claude escreve o arquivo antes do CLI publicar | Opção A: sem flags novas no CLI. CLI publica o que encontra no arquivo local. |
| CLI mantém `strip` + `normalize_body` como safety net | Evita vazar paths locais ou `project_name` no hub caso Claude esqueça algo. |
| `_show_diff()` mantido como informativo no CLI | Mostra o resultado pós-normalização. Sem `input()` de confirmação — Claude já confirmou. |
| `version` não é alterada por Claude | Bump de versão é responsabilidade exclusiva do CLI (`files.bump_version()`). |
| Sem flags novas no CLI | Toda lógica de seleção e merge está no `command.md`. CLI apenas valida, limpa e publica. |

---

## Arquivos a modificar

### `cli/commands/publish_resource.py`
- Adicionar validação de `CLAUDE.md` antes de qualquer operação
- Adicionar flag `--validate-only`: executa apenas validação e encerra (sem publicar)
- Remover `input()` de confirmação — Claude trata confirmação no `command.md`
- Manter `_show_diff()` como informativo (sem prompt)
- Após publicação: atualizar `source: hub/<tipo>s/<nome>@<versão>` no arquivo local
  ```python
  frontmatter.write(src, {
      "version": version,
      "source": f"hub/{resource_type}s/{name}@{version}",
  })
  ```

### `cli/commands/build_resource.py`
- Adicionar validação de `CLAUDE.md`:
  ```python
  if not (dest_dir / "CLAUDE.md").exists():
      raise FileNotFoundError(
          f"Projeto não encontrado em: {dest_dir}\n"
          f"  Use --dest <caminho> para especificar o projeto"
      )
  ```

### `hub/commands/build-resource/command.md`
- Adicionar Passo 1: resolver caminho do projeto
- Executar com `--dest "<projeto>/.claude"`

### `hub/commands/publish-resource/command.md`
- Reescrever completamente conforme fases 1, 3 e 4 acima

### `~/.claude/commands/build-resource.md`
- Sincronizar com hub após atualização

### `~/.claude/commands/publish-resource.md`
- Sincronizar com hub após atualização

---

## Verificação

1. **Novo recurso — skill**: criar skill no Dog via `/build-resource` → publicar via `/publish-resource` → confirmar ID atribuído, arquivo em `hub/skills/`, `source` local atualizado para `hub/skills/<nome>@1.0.0`
2. **Novo recurso — command**: mesmo fluxo com tipo command
3. **Atualização — skill instalada do hub**: instalar `ux-writing-review` no Cat, editar, publicar → confirmar aviso de impacto, lista de mudanças por seção, seleção granular, revisão do pacote, bump de versão
4. **Proxy ignorado**: confirmar que `.claude/commands/<name>.md` (proxy) não aparece na listagem nem é publicado
5. **Cancelamento em qualquer ponto**: responder `n` → confirmar que hub não foi alterado e arquivo local também não
6. **Safety net CLI**: confirmar que mesmo se Claude escrever `project` no arquivo, o CLI remove antes de publicar no hub
