---
title: cli-prepare-pattern
type: plan
status: draft
created: 2026-05-16
updated: 2026-05-16
---

# Plano — Padrão `--prepare`: Python como fonte de contexto dos commands

## Contexto

Os commands do hub (`command.md`) hoje misturam dois tipos de instrução:

1. **Lógica computável** — detectar diretório atual, listar recursos existentes, inferir padrão de nomes, extrair tags de frontmatter. Está em markdown e depende de Claude interpretar e executar corretamente.
2. **UX com o usuário** — apresentar opções via `AskUserQuestion`, coletar escolhas, guardar variáveis. Não pode ser movido para Python — depende de ferramentas do Claude.

O problema: lógica computável em markdown é não-determinística. Claude pode interpretar de forma diferente entre sessões, pular etapas, ou gerar sugestões incorretas.

---

## Decisão

Adotar o padrão `--prepare`: o CLI expõe um modo de preparação que computa todo o contexto determinístico antes do diálogo começar. O resultado é JSON. Claude lê o JSON e usa os valores prontos para popular `AskUserQuestion` — sem inferência sobre estrutura de arquivos, sem interpretação de listagens.

**Antes:**
```
command.md instrui Claude a:
  1. Rodar ls, ler output, inferir padrão → gerar sugestões
  2. Apresentar sugestões via AskUserQuestion
```

**Depois:**
```
command.md instrui Claude a:
  1. Rodar --prepare → ler JSON com contexto computado
  2. Usar valores do JSON para popular AskUserQuestion
  3. Gerar sugestões de linguagem natural (description) com base no JSON
```

---

## Divisão de responsabilidades

| Responsabilidade | Quem faz | Por quê |
|---|---|---|
| Detectar diretório atual | Python | Determinístico — `Path.cwd()` |
| Listar resources instalados | Python | Determinístico — leitura de arquivos |
| Detectar padrão de nomenclatura | Python | Heurística sobre nomes existentes |
| Extrair tags existentes | Python | Parsing de frontmatter |
| **Gerar sugestões de nome** | **Híbrido** | Python detecta padrão + exemplos; Claude gera variações semanticamente relevantes |
| **Gerar variações de description** | **Claude** | Geração de linguagem natural — Claude faz melhor |
| Apresentar opções ao usuário | Claude | `AskUserQuestion` é ferramenta do Claude |
| Executar criação/instalação | Python | Determinístico — CLI |

---

## Contrato do modo `--prepare`

### Saída

- **Stdout:** JSON puro — nunca misturar com texto humano
- **Stderr:** vazio sempre
- **Exit code:** sempre 0 — erros são retornados no JSON, nunca via exceção

### Formato de sucesso

```json
{
  "context": { ... },
  "suggestions": { ... },
  "meta": { ... }
}
```

### Formato de erro

```json
{
  "error": "mensagem descritiva do problema"
}
```

Claude verifica se `"error"` está presente no JSON antes de prosseguir. Se sim, reporta ao usuário e encerra.

### Tratamento de exceções em `--prepare`

O handler global de `main.py:24` imprime para stderr e sai com código 1 — incompatível com o contrato. Cada `run()` que suportar `--prepare` deve envolver o bloco prepare em `try/except` próprio:

```python
if args.prepare:
    try:
        result = _prepare(args)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
    return
```

---

## Pré-requisitos

### 1. Corrigir `frontmatter.read()` — parsing de listas

`cli/utils/frontmatter.py:read()` parseia `tags: [review, ux]` como string `"[review, ux]"`, não como lista Python. O `--prepare` precisa extrair tags de resources existentes corretamente.

**Alteração em `read()`:**

```python
# após o split key/value:
if v.startswith('[') and v.endswith(']'):
    value = [x.strip() for x in v[1:-1].split(',') if x.strip()]
else:
    value = v
```

Cobrir com teste em `cli/tests/test_frontmatter.py`. Essa correção beneficia todos os comandos que leem tags.

### 2. Adicionar `version` em `_collect_hub()` e `_collect_installed()`

`list_resources.py:_collect_hub()` retorna `id`, `name`, `description` — sem `version`. A Fase 3 precisa de `version` para comparar disponível vs instalado.

**Alteração em `_collect_hub()` para tipos md:**

```python
fm = frontmatter.read(md)
rows.append({
    "id": fm.get("id", ""),
    "name": d.name,
    "version": fm.get("version", ""),
    "description": fm.get("description", ""),
})
```

**Alteração em `_collect_installed()` para skills/agents:**

```python
fm = frontmatter.read(f)
rows.append({
    "name": f.stem,
    "version": fm.get("version", ""),
    "description": fm.get("description", ""),
})
```

Cobrir com testes em `cli/tests/test_integrity.py` ou novo `test_list_resources.py`.

---

## Escopo

| Command | Lógica a mover para Python | Módulo Python |
|---|---|---|
| `build-resource` | Padrão de nomes, tags existentes | `build_resource.py` — adicionar `--prepare` |
| `setup-claude` | Detecção de projetos irmãos | `setup_claude.py` — criar do zero + registrar em `main.py` |
| `install-resource` | Listar disponíveis vs instalados | `install_resource.py` — adicionar `--prepare`, reusar `list_resources.py` |

---

## Plano de execução

### Fase 0 — Pré-requisitos

1. Corrigir `frontmatter.read()` com parsing de listas + teste
2. Adicionar `version` em `_collect_hub()` e `_collect_installed()` + teste

---

### Fase 1 — `build-resource --prepare`

**Arquivo:** `build_resource.py`

#### Argparse

`--name` é obrigatório no modo normal mas proibido em `--prepare`. Solução: tornar `--name` opcional no `register()` e validar manualmente em `run()`:

```python
p.add_argument("--name", default="", help="Nome do recurso (obrigatório fora do modo --prepare)")
p.add_argument("--prepare", action="store_true")

# em run():
if not args.prepare and not args.name:
    raise ValueError("--name é obrigatório fora do modo --prepare")
```

#### O que `--prepare` computa

| Campo JSON | Lógica Python |
|---|---|
| `context.current_path` | `str(Path(dest).parent)` |
| `context.project_name` | `frontmatter.read(dest/"CLAUDE.md").get("name", "")` |
| `meta.has_existing_resources` | `bool(existing_names)` |
| `meta.existing_names` | Nomes dos `.md` em `dest/<tipo>s/` — lista vazia se pasta não existir |
| `meta.naming_pattern` | Heurística sobre `existing_names` (ver abaixo) |
| `suggestions.tags` | Tags extraídas de resources instalados (ver abaixo) |

#### Heurística de `naming_pattern`

```python
def _infer_naming_pattern(names: list[str]) -> str:
    if not names:
        return "<nome>"
    part_counts = [len(n.split('-')) for n in names]
    most_common = max(set(part_counts), key=part_counts.count)
    return '-'.join([f'<parte-{i+1}>' for i in range(most_common)])
```

Exemplos: `["ux-writing-review", "code-review"]` → partes: `[3, 2]` → mais comum: ambos empatados → usa o maior → `"<parte-1>-<parte-2>-<parte-3>"`. Claude usa isso como guia, não como template rígido.

#### Heurística de `suggestions.tags`

```python
def _extract_tag_suggestions(dest: Path) -> list[list[str]]:
    # lê tags de skills e agents instalados
    counter = {}
    for folder in ["skills", "agents"]:
        for f in (dest / folder).glob("*.md") if (dest / folder).exists() else []:
            tags = frontmatter.read(f).get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    counter[tag] = counter.get(tag, 0) + 1
    # ordena por frequência, divide em grupos de até 3
    sorted_tags = sorted(counter, key=counter.get, reverse=True)
    groups = [sorted_tags[i:i+3] for i in range(0, min(len(sorted_tags), 9), 3)]
    return groups[:3]
```

#### JSON de saída

```json
{
  "context": {
    "current_path": "/Users/.../MeuProjeto",
    "project_name": "Meu Projeto"
  },
  "meta": {
    "has_existing_resources": true,
    "naming_pattern": "<parte-1>-<parte-2>",
    "existing_names": ["ux-writing-review", "code-review"]
  },
  "suggestions": {
    "tags": [
      ["ux", "review", "interface"],
      ["branding", "content"],
      ["design"]
    ]
  }
}
```

#### Alterações no `command.md` do `build-resource`

- **Passo 3 (nome):** rodar `--prepare --type <tipo> --dest <projeto>/.claude`, ler JSON. Instruir Claude: *"Com base no padrão `{meta.naming_pattern}` e exemplos `{meta.existing_names}`, gere até 3 sugestões de nome."* Popular `AskUserQuestion` com as sugestões geradas + "Outro (digitar)". Se `meta.has_existing_resources` for `false`: perguntar em texto livre.
- **Pós-execução (tags):** usar `suggestions.tags` do JSON já computado para popular `AskUserQuestion` com `multiSelect: true`. Se `suggestions.tags` for vazio: perguntar em texto livre.
- **Passo 1** permanece em markdown — define `<projeto>` antes do `--prepare`.

---

### Fase 2 — `setup-claude --prepare`

**Contexto:** `setup-claude` não tem módulo Python. Esta fase cria o módulo do zero.

**Arquivos afetados:**
- Criar `cli/commands/setup_claude.py`
- Adicionar import e `setup_claude.register(sub)` em `cli/main.py`

#### Escopo do módulo `setup_claude.py`

O módulo terá apenas o subcomando `--prepare` nesta fase. A lógica de criação de projeto (CLAUDE.md, project-details) permanece no `command.md` e no `new_project.py` existente — `setup-claude` orquestra via Claude, não via CLI próprio.

#### O que `--prepare` computa

| Campo JSON | Lógica Python |
|---|---|
| `context.current_path` | `str(Path.cwd())` |
| `suggestions.project_paths` | `Path.cwd()` + pastas irmãs cujo pai contém `.claude/CLAUDE.md`; máximo 3 total |

```python
def _find_candidate_paths(base: Path) -> list[str]:
    candidates = [str(base)]
    parent = base.parent
    for sibling in sorted(parent.iterdir()):
        if sibling == base or not sibling.is_dir():
            continue
        if (sibling / ".claude" / "CLAUDE.md").exists():
            candidates.append(str(sibling))
        if len(candidates) == 3:
            break
    return candidates
```

#### JSON de saída

```json
{
  "context": {
    "current_path": "/Users/.../MeuProjeto"
  },
  "suggestions": {
    "project_paths": [
      "/Users/.../MeuProjeto",
      "/Users/.../OutroProjeto"
    ]
  }
}
```

#### Alterações no `command.md` do `setup-claude`

- Passo 2: rodar `python -m cli setup-claude --prepare`, usar `suggestions.project_paths` para popular `AskUserQuestion` (máximo 3 opções + "Informar outro caminho")
- Remove instrução atual de `ls` + inferência manual de pastas irmãs

---

### Fase 3 — `install-resource --prepare`

**Contexto:** `list_resources.py` já implementa `_collect_hub()` e `_collect_installed()`. Não reimplementar — importar e reutilizar após adicionar `version` nos retornos (Fase 0, pré-requisito 2).

**Arquivo:** `install_resource.py`

#### Argparse

```python
p.add_argument("--prepare", action="store_true")
# --name já é obrigatório; tornar opcional e validar manualmente (mesmo padrão da Fase 1)
```

#### O que `--prepare` computa

```python
from cli.commands import list_resources

available = list_resources._collect_hub(hub, resource_type)
installed = list_resources._collect_installed(dest_dir, resource_type)
```

#### JSON de saída

```json
{
  "available": [
    {"name": "ux-writing-review", "version": "1.3.0", "description": "Revisa copy..."},
    {"name": "translate-pt-to-eng", "version": "1.0.0", "description": "Traduz..."}
  ],
  "installed": [
    {"name": "ux-writing-review", "version": "1.2.0"}
  ]
}
```

Claude usa `available` para listar opções e indica versão instalada quando o nome aparece em `installed`.

#### Alterações no `command.md` do `install-resource`

- Substituir listagem manual por: rodar `--prepare --type <tipo> --dest <projeto>/.claude`, usar JSON para popular `AskUserQuestion` com status de instalação visível

---

## Compatibilidade com o Python existente

| Ponto | Status |
|---|---|
| `config.dest_dir_for_type()` | Compatível — reutilizado sem alteração |
| `frontmatter.write()`, `frontmatter.inject()` | Não afetados |
| `main.py` error handling | `--prepare` captura exceções internamente — não propaga para `main.py` |
| `list_resources._collect_hub/installed()` | Reutilizados na Fase 3 após adicionar `version` na Fase 0 |
| Saída stdout atual (print) | `--prepare` usa `print(json.dumps(...))` — compatível |
| `--name` obrigatório em argparse | Tornar opcional + validação manual em `run()` — padrão consistente nas Fases 1 e 3 |

---

## Testes

| Fase | O que testar | Arquivo |
|---|---|---|
| 0 | `frontmatter.read()` com tags como lista | `test_frontmatter.py` |
| 0 | `_collect_hub()` retorna `version` | `test_list_resources.py` (novo) |
| 0 | `_collect_installed()` retorna `version` | `test_list_resources.py` (novo) |
| 1 | `build-resource --prepare` retorna JSON válido com projeto vazio | `test_build_resource.py` (novo) |
| 1 | `build-resource --prepare` retorna JSON com nomes e tags existentes | `test_build_resource.py` (novo) |
| 1 | `build-resource --prepare` retorna `{"error": ...}` se `CLAUDE.md` ausente | `test_build_resource.py` (novo) |
| 2 | `setup-claude --prepare` retorna caminho atual + irmãos válidos | `test_setup_claude.py` (novo) |
| 3 | `install-resource --prepare` retorna available e installed sem duplicar lógica | `test_install_resource.py` (novo) |

---

## Ordem de implementação

1. **Fase 0** — pré-requisitos: `frontmatter.read()` + `version` em `list_resources`. Desbloqueia todas as fases.
2. **Fase 1** — `build-resource --prepare`. Maior impacto, valida o padrão completo incluindo o contrato de erro.
3. **Fase 2** — `setup-claude --prepare`. Menor escopo, cria módulo do zero.
4. **Fase 3** — `install-resource --prepare`. Depende da Fase 0 (versões); reutiliza `list_resources.py`.
