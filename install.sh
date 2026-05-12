#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# DEPRECATED — install.sh será removido após período de validação.
# Use o módulo Python:
#   python -m cli <comando> [argumentos]
#   python -m cli --help
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# install.sh — Gerenciador de recursos Claude (legado)
# Uso: install.sh <comando> [tipo] [nome] [flags]
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY="$(date +%Y-%m-%d)"
DRY_RUN=false
GLOBAL=false
STACK="nextjs-supabase-vercel-claude"
DEST_DIR=""  # definido após parse de flags

# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

header() { printf '\n%s\n' "$*"; }
info()   { printf '  -> %s\n' "$*"; }
ok()     { printf '  [ok] %s\n' "$*"; }
warn()   { printf '  [aviso] %s\n' "$*"; }
err()    { printf '  [erro] %s\n' "$*" >&2; }
die()    { err "$*"; exit 1; }

confirm() {
  local msg="$1"
  local answer
  printf '%s [s/n] ' "$msg"
  read -r answer
  [[ "$answer" == "s" || "$answer" == "S" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# Utilitários compartilhados
# ─────────────────────────────────────────────────────────────────────────────

# ─── Mapeamento tipo → diretório ─────────────────────────────────────────────

dest_dir_for_type() {
  local type="$1" base="$2"
  case "$type" in
    skill)       echo "$base/skills" ;;
    agent)       echo "$base/agents" ;;
    hook)        echo "$base/hooks" ;;
    command)     echo "$base/commands" ;;
    plugin)      echo "$base/plugins" ;;
    instruction) echo "$base" ;;
    *) die "Tipo desconhecido: $type" ;;
  esac
}

hub_source_dir() {
  local type="$1" name="$2"
  case "$type" in
    skill)       echo "$SCRIPT_DIR/hub/skills/$name" ;;
    agent)       echo "$SCRIPT_DIR/hub/agents/$name" ;;
    hook)        echo "$SCRIPT_DIR/hub/hooks/$name" ;;
    command)     echo "$SCRIPT_DIR/hub/commands/$name" ;;
    plugin)      echo "$SCRIPT_DIR/hub/plugins/$name" ;;
    instruction) echo "$SCRIPT_DIR/hub/instructions" ;;
    *) die "Tipo desconhecido: $type" ;;
  esac
}

hub_main_file() {
  local type="$1" name="$2"
  local dir
  dir="$(hub_source_dir "$type" "$name")"
  case "$type" in
    skill)       echo "$dir/skill.md" ;;
    agent)       echo "$dir/agent.md" ;;
    hook)        echo "$dir/hook.json" ;;
    command)     echo "$dir/command.md" ;;
    plugin)      echo "$dir/plugin.json" ;;
    instruction) echo "$dir/$name.md" ;;
    *) die "Tipo desconhecido: $type" ;;
  esac
}

template_dir_for_type() {
  local type="$1"
  case "$type" in
    skill)   echo "$SCRIPT_DIR/build/01-skills/_template" ;;
    agent)   echo "$SCRIPT_DIR/build/03-agents/_template" ;;
    hook)    echo "$SCRIPT_DIR/build/02-hooks/_template" ;;
    command) echo "$SCRIPT_DIR/build/04-plugins/_template/commands" ;;
    plugin)  echo "$SCRIPT_DIR/build/04-plugins/_template" ;;
    *) die "Tipo desconhecido: $type. Tipos válidos para build-resource: skill, agent, hook, command, plugin" ;;
  esac
}

# ─── Frontmatter (YAML) ──────────────────────────────────────────────────────

get_frontmatter_field() {
  local file="$1" field="$2"
  python3 - "$file" "$field" <<'EOF'
import re, sys
file, field = sys.argv[1], sys.argv[2]
content = open(file).read()
m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if not m:
    sys.exit(0)
match = re.search(rf'^{re.escape(field)}:\s*(.+)$', m.group(1), re.MULTILINE)
if match:
    print(match.group(1).strip())
EOF
}

get_json_field() {
  local file="$1" field="$2"
  python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],''))" \
    "$file" "$field" 2>/dev/null || echo ""
}

get_project_name() {
  local claude_md="$DEST_DIR/CLAUDE.md"
  [[ -f "$claude_md" ]] && get_frontmatter_field "$claude_md" "name" || echo ""
}

util_inject_frontmatter() {
  local file="$1" project="$2" source="$3"
  python3 - "$file" "$project" "$source" "$TODAY" <<'EOF'
import re, sys
file, project, source, today = sys.argv[1:5]
content = open(file).read()

m = re.match(r'^(---\n)(.*?)(\n---)', content, re.DOTALL)
if not m:
    sys.exit(0)

fm = m.group(2)

def set_field(text, key, value):
    pattern = rf'^{re.escape(key)}:.*$'
    repl = f'{key}: {value}'
    if re.search(pattern, text, re.MULTILINE):
        return re.sub(pattern, repl, text, flags=re.MULTILINE)
    if '# system' in text:
        return re.sub(r'(# system)', rf'{repl}\n\1', text, count=1)
    return text + f'\n{repl}'

fm = set_field(fm, 'project', project)
fm = set_field(fm, 'created', today)
fm = set_field(fm, 'source', source)

open(file, 'w').write(m.group(1) + fm + m.group(3) + content[m.end():])
EOF
}

util_strip_frontmatter() {
  local file="$1"
  python3 - "$file" <<'EOF'
import re, sys
file = sys.argv[1]
content = open(file).read()

m = re.match(r'^(---\n)(.*?)(\n---)', content, re.DOTALL)
if not m:
    sys.exit(0)

fm = m.group(2)

for field in ['project', 'source']:
    fm = re.sub(rf'^{re.escape(field)}:.*\n?', '', fm, flags=re.MULTILINE)

# scope: project → global ao publicar no hub
fm = re.sub(r'^scope:.*$', 'scope: global', fm, flags=re.MULTILINE)

fm = re.sub(r'\n{3,}', '\n\n', fm).strip()
open(file, 'w').write(m.group(1) + fm + m.group(3) + content[m.end():])
EOF
}

util_normalize_body() {
  local file="$1" project_name="$2"
  python3 - "$file" "$project_name" <<'EOF'
import re, sys
file, project = sys.argv[1], sys.argv[2]
content = open(file).read()

m = re.match(r'^(---\n.*?\n---\n)', content, re.DOTALL)
if m:
    header = m.group(1)
    body = content[m.end():]
else:
    header, body = '', content

body = re.sub(r'/(?:Users|home)/\S+', '<path>', body)

if project:
    body = body.replace(project, '<project-name>')

open(file, 'w').write(header + body)
EOF
}

util_bump_version() {
  local version="$1"
  python3 -c "
v = '$version'.split('.')
if len(v) == 3:
    v[2] = str(int(v[2]) + 1)
    print('.'.join(v))
else:
    print('$version')
" 2>/dev/null || echo "$version"
}

util_set_frontmatter_field() {
  local file="$1" field="$2" value="$3"
  python3 - "$file" "$field" "$value" <<'EOF'
import re, sys
file, field, value = sys.argv[1:4]
content = open(file).read()

m = re.match(r'^(---\n)(.*?)(\n---)', content, re.DOTALL)
if not m:
    sys.exit(0)

fm = m.group(2)
pattern = rf'^{re.escape(field)}:.*$'
repl = f'{field}: {value}'
fm = re.sub(pattern, repl, fm, flags=re.MULTILINE)
open(file, 'w').write(m.group(1) + fm + m.group(3) + content[m.end():])
EOF
}

# ─── Resolução de conflito de versão ─────────────────────────────────────────

util_copy_versioned() {
  local src="$1" dest="$2" label="$3" v_src="${4:-}" v_dest="${5:-}"

  if [[ -f "$dest" ]]; then
    [[ -z "$v_dest" ]] && v_dest="$(get_frontmatter_field "$dest" "version" 2>/dev/null || echo "?")"
    [[ -z "$v_src"  ]] && v_src="$(get_frontmatter_field "$src"  "version" 2>/dev/null || echo "?")"

    if [[ "$DRY_RUN" == true ]]; then
      info "[dry-run] $label já instalado (atual: $v_dest, novo: $v_src) — seria sobrescrito"
      return 0
    fi

    printf '\n  Recurso %s já instalado (atual: %s, novo: %s).\n' \
      "$label" "$v_dest" "$v_src"
    printf '  [s] sobrescrever  [p] pular  [c] cancelar: '
    read -r choice

    case "$choice" in
      [Ss]) : ;;
      [Pp]) info "Pulando $label"; return 1 ;;
      *) die "Cancelado." ;;
    esac
  else
    [[ "$DRY_RUN" == true ]] && { info "[dry-run] $src -> $dest"; return 0; }
  fi

  mkdir -p "$(dirname "$dest")"
  cp "$src" "$dest"
}

# ─── Edição de settings.json ─────────────────────────────────────────────────

util_edit_settings_json() {
  local settings_file="$1" hook_name="$2" hook_json_file="$3"

  local updated
  updated="$(python3 - "$settings_file" "$hook_name" "$hook_json_file" <<'EOF'
import json, sys
settings_file, hook_name, hook_json_file = sys.argv[1:4]

try:
    with open(settings_file) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

with open(hook_json_file) as f:
    hook_meta = json.load(f)

event   = hook_meta.get('event', 'PostToolUse')
matcher = hook_meta.get('matcher', {}).get('tool', '*')

new_hook = {
    'type': 'command',
    'command': f'bash .claude/hooks/{hook_name}/hook.sh'
}
new_block = {'matcher': matcher, 'hooks': [new_hook]}

hooks      = settings.setdefault('hooks', {})
event_list = hooks.setdefault(event, [])

for block in event_list:
    for h in block.get('hooks', []):
        if h.get('command') == new_hook['command']:
            print(json.dumps(settings, indent=2, ensure_ascii=False))
            sys.exit(0)

event_list.append(new_block)
print(json.dumps(settings, indent=2, ensure_ascii=False))
EOF
)"

  header "Alterações em $settings_file:"
  if [[ -f "$settings_file" ]]; then
    diff <(cat "$settings_file") <(echo "$updated") || true
  else
    echo "$updated"
  fi
  echo ""

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] settings.json não alterado"
    return 0
  fi

  confirm "Aplicar alterações em settings.json?" || { info "Alterações ignoradas"; return 0; }
  echo "$updated" > "$settings_file"
  ok "settings.json atualizado"
}

# ─── Registry ────────────────────────────────────────────────────────────────

util_update_registry() {
  local type="$1" name="$2" version="$3" description="$4" tags="$5"

  [[ "$DRY_RUN" == true ]] && { info "[dry-run] registry.json não atualizado"; return 0; }

  python3 - "$SCRIPT_DIR/registry.json" "$type" "$name" \
            "$version" "$description" "$tags" "$TODAY" <<'EOF'
import json, sys
registry_file, type_, name, version, description, tags, today = sys.argv[1:8]

with open(registry_file) as f:
    reg = json.load(f)

type_key = f'{type_}s'
reg.setdefault(type_key, [])

entry = {
    'name': name,
    'version': version,
    'description': description,
    'tags': [t.strip() for t in tags.strip('[]').split(',') if t.strip()],
    'updated': today
}

for i, item in enumerate(reg[type_key]):
    if item.get('name') == name:
        reg[type_key][i] = entry
        break
else:
    reg[type_key].append(entry)

reg['updated'] = today

with open(registry_file, 'w') as f:
    json.dump(reg, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF
  ok "registry.json atualizado"
}

# ─── Validação para publish ───────────────────────────────────────────────────

util_validate_for_publish() {
  local file="$1"
  local errors=0

  for field in name type version description; do
    local val
    val="$(get_frontmatter_field "$file" "$field" 2>/dev/null || echo "")"
    if [[ -z "$val" || "$val" == '""' || "$val" == "(preencher)" ]]; then
      err "Campo obrigatório ausente ou vazio: $field"
      errors=$((errors + 1))
    fi
  done

  for field in author tags; do
    local val
    val="$(get_frontmatter_field "$file" "$field" 2>/dev/null || echo "")"
    if [[ -z "$val" || "$val" == "[]" || "$val" == '""' ]]; then
      warn "Campo recomendado vazio: $field"
    fi
  done

  [[ $errors -gt 0 ]] && die "$errors erro(s) — preencha os campos obrigatórios antes de publicar"
  return 0
}

# ─── Changelog ───────────────────────────────────────────────────────────────

append_changelog() {
  local type="$1" name="$2" version="$3"
  local changelog="$SCRIPT_DIR/CHANGELOG.md"
  [[ -f "$changelog" ]] || return 0

  python3 - "$changelog" "$type" "$name" "$version" "$TODAY" <<'EOF'
import sys
changelog, type_, name, version, today = sys.argv[1:6]
content = open(changelog).read()
entry = f'- [{today}] [{type_}] {name} v{version} — publicado no hub\n'
marker = '<!-- Recursos em desenvolvimento ou aguardando publicação no hub. -->'
content = content.replace(marker, marker + '\n' + entry)
open(changelog, 'w').write(content)
EOF
  ok "CHANGELOG.md atualizado"
}

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 1 — claude-start: setup global da máquina
# ─────────────────────────────────────────────────────────────────────────────

cmd_init() {
  header "Setup global do ambiente Claude"

  local dest="$HOME/.claude"

  # Verificar dependência obrigatória
  command -v python3 &>/dev/null || die "python3 não encontrado — necessário para o install.sh"

  # Verificar arquivos fonte
  [[ -f "$SCRIPT_DIR/global/CLAUDE.md" ]]    || die "Não encontrado: global/CLAUDE.md"
  [[ -f "$SCRIPT_DIR/global/settings.json" ]] || die "Não encontrado: global/settings.json"

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] hub-path -> $dest/hub-path ($SCRIPT_DIR)"
    info "[dry-run] global/CLAUDE.md -> $dest/CLAUDE.md"
    info "[dry-run] global/settings.json -> $dest/settings.json"
    for cmd_dir in "$SCRIPT_DIR/hub/commands"/*/; do
      local cmd_name
      cmd_name="$(basename "$cmd_dir")"
      [[ -f "$cmd_dir/command.md" ]] || continue
      info "[dry-run] comando $cmd_name -> $dest/commands/$cmd_name.md"
    done
    return 0
  fi

  mkdir -p "$dest" "$dest/commands"

  local changed=0

  # hub-path — detectar mudança antes de sobrescrever
  if [[ -f "$dest/hub-path" ]]; then
    local existing_path
    existing_path="$(cat "$dest/hub-path")"
    if [[ "$existing_path" != "$SCRIPT_DIR" ]]; then
      warn "hub-path existente aponta para: $existing_path"
      warn "Novo valor: $SCRIPT_DIR"
      if confirm "Atualizar hub-path?"; then
        echo "$SCRIPT_DIR" > "$dest/hub-path"
        ok "hub-path atualizado: $dest/hub-path"
        changed=$((changed + 1))
      else
        info "hub-path mantido: $existing_path"
      fi
    else
      info "hub-path já correto — mantido"
    fi
  else
    echo "$SCRIPT_DIR" > "$dest/hub-path"
    ok "hub-path salvo: $dest/hub-path"
    changed=$((changed + 1))
  fi

  # CLAUDE.md e settings.json
  for f in CLAUDE.md settings.json; do
    local src="$SCRIPT_DIR/global/$f" target="$dest/$f"
    if [[ -f "$target" ]]; then
      if [[ "$f" == "CLAUDE.md" ]]; then
        local v_hub v_local
        v_hub="$(get_frontmatter_field   "$src"    "version" 2>/dev/null || echo "")"
        v_local="$(get_frontmatter_field "$target" "version" 2>/dev/null || echo "")"
        if [[ -n "$v_hub" && -n "$v_local" && "$v_hub" != "$v_local" ]]; then
          warn "CLAUDE.md desatualizado — local: $v_local, hub: $v_hub (edite manualmente se necessário)"
        else
          info "CLAUDE.md já existe — mantido"
        fi
      else
        info "$f já existe — mantido"
      fi
    else
      cp "$src" "$target"
      ok "$f instalado: $target"
      changed=$((changed + 1))
    fi
  done

  # Comandos globais — instalar/atualizar em ~/.claude/commands/
  for cmd_dir in "$SCRIPT_DIR/hub/commands"/*/; do
    local cmd_name cmd_src cmd_dest
    cmd_name="$(basename "$cmd_dir")"
    cmd_src="$cmd_dir/command.md"
    cmd_dest="$dest/commands/$cmd_name.md"
    [[ -f "$cmd_src" ]] || continue

    if [[ -f "$cmd_dest" ]]; then
      local v_hub v_local
      v_hub="$(get_frontmatter_field   "$cmd_src"  "version" 2>/dev/null || echo "?")"
      v_local="$(get_frontmatter_field "$cmd_dest" "version" 2>/dev/null || echo "?")"
      if [[ "$v_hub" != "$v_local" ]]; then
        cp "$cmd_src" "$cmd_dest"
        ok "Comando atualizado: $cmd_name ($v_local -> $v_hub)"
        changed=$((changed + 1))
      else
        info "Comando já atualizado: $cmd_name ($v_local)"
      fi
    else
      cp "$cmd_src" "$cmd_dest"
      ok "Comando instalado: $cmd_name"
      changed=$((changed + 1))
    fi
  done

  if [[ $changed -eq 0 ]]; then
    info "Ambiente global já configurado — nenhuma alteração feita"
  else
    ok "Ambiente global configurado ($changed alteração(ões))"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 2 — setup-claude: configura novo projeto
# ─────────────────────────────────────────────────────────────────────────────

cmd_init_project() {
  local project_name="${1:-}"
  [[ -n "$project_name" ]] || die "Nome do projeto obrigatório: install.sh setup-claude <nome>"

  header "Configurando projeto: $project_name"

  local dirs=(commands skills agents hooks plugins)

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] criaria $DEST_DIR/ com subpastas: ${dirs[*]}"
    info "[dry-run] geraria CLAUDE.md com name=$project_name"
    local frag_count
    frag_count="$(ls "$SCRIPT_DIR/build/00-claude-md/fragments/"*.md 2>/dev/null | wc -l | tr -d ' ')"
    info "[dry-run] injetaria $frag_count fragmentos"
    info "[dry-run] copiaria settings.json base"
    info "[dry-run] criaria design/ e dev/ com READMEs"
    return 0
  fi

  for d in "${dirs[@]}"; do mkdir -p "$DEST_DIR/$d"; done

  local claude_md="$DEST_DIR/CLAUDE.md"
  if [[ -f "$claude_md" ]]; then
    info "CLAUDE.md já existe — mantido (projeto já configurado)"
    ok "Projeto '$project_name' verificado em $DEST_DIR/"
    _create_project_folders "$project_name"
    return 0
  fi

  cp "$SCRIPT_DIR/build/00-claude-md/project.md" "$claude_md"

  python3 - "$claude_md" "$project_name" "$STACK" "$TODAY" <<'EOF'
import re, sys
file, project_name, stack, today = sys.argv[1:5]
content = open(file).read()

def set_field(text, key, value):
    pattern = rf'^{re.escape(key)}:.*$'
    repl = f'{key}: {value}'
    if re.search(pattern, text, re.MULTILINE):
        return re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text

content = set_field(content, 'name', project_name)
content = set_field(content, 'status', 'stable')
content = set_field(content, 'project', project_name)
content = set_field(content, 'created', today)
content = set_field(content, 'updated', today)
content = set_field(content, 'tags', f'[{stack}]')
content = set_field(content, 'stack', stack)
content = content.replace('[NOME DO PROJETO]', project_name)
content = content.replace('(preencher)', '""')

open(file, 'w').write(content)
EOF

  ok "CLAUDE.md gerado"

  local fragments_dir="$SCRIPT_DIR/build/00-claude-md/fragments"
  if [[ -d "$fragments_dir" ]]; then
    local fragment_order=(language.md communication.md execution.md anti-hallucination.md tools.md frontmatter.md)
    for frag in "${fragment_order[@]}"; do
      local frag_path="$fragments_dir/$frag"
      [[ -f "$frag_path" ]] || continue
      printf '\n---\n\n' >> "$claude_md"
      python3 - "$frag_path" >> "$claude_md" <<'PYEOF'
import sys, re
content = open(sys.argv[1]).read()
content = re.sub(r'^---\n.*?---\n', '', content, flags=re.DOTALL).strip()
print(content)
PYEOF
    done
    ok "Fragmentos incluídos"
  fi

  local settings="$DEST_DIR/settings.json"
  if [[ ! -f "$settings" ]]; then
    cp "$SCRIPT_DIR/global/settings.json" "$settings"
    ok "settings.json copiado"
  else
    info "settings.json já existe — mantido"
  fi

  ok "Projeto '$project_name' configurado em $DEST_DIR/"

  _create_project_folders "$project_name"
}

_create_project_folders() {
  local project_name="${1:-}"
  local project_dir
  project_dir="$(dirname "$DEST_DIR")"

  header "Criando estrutura de pastas do projeto"

  local design_dirs=(
    "design/01-branding/research"
    "design/01-branding/plan"
    "design/01-branding/create"
    "design/02-product/discovery"
    "design/02-product/ux-ui"
  )

  for d in "${design_dirs[@]}"; do
    mkdir -p "$project_dir/$d"
  done

  _write_readme "$project_dir/design" \
    "Design" \
    "Assets de marca e design do produto."

  _write_readme "$project_dir/design/01-branding" \
    "Identidade visual da marca" \
    "Pesquisa, planejamento e produção dos assets de marca."

  _write_readme "$project_dir/design/01-branding/research" \
    "Pesquisa de marca" \
    "Resultados de pesquisa e discovery de marca: benchmarking, moodboard e insights."

  _write_readme "$project_dir/design/01-branding/plan" \
    "Estratégia de marca" \
    "Estratégia da marca: posicionamento, voz, tom e diretrizes."

  _write_readme "$project_dir/design/01-branding/create" \
    "Assets de marca" \
    "Todos os assets produzidos: tokens de design, expressão visual, expressão verbal e direção criativa."

  _write_readme "$project_dir/design/02-product" \
    "Design do produto digital" \
    "Discovery com usuários e design de interface do produto."

  _write_readme "$project_dir/design/02-product/discovery" \
    "Discovery de produto" \
    "Pesquisa com usuários, personas, jornadas e definição de requisitos."

  _write_readme "$project_dir/design/02-product/ux-ui" \
    "UX/UI" \
    "Wireframes, protótipos e interfaces finais do produto."

  ok "design/ criado"

  _create_dev_nextjs_supabase "$project_dir"
}

_write_readme() {
  local dir="$1" title="$2" description="$3"
  local readme="$dir/README.md"
  [[ -f "$readme" ]] && return 0
  local name
  name="$(basename "$dir")"
  cat > "$readme" <<EOF
---
# about
name: $name
type: readme
project: ""
description: $description
tags: []

# history
author: ""
created: $TODAY
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

# $title

$description
EOF
}

_create_dev_nextjs_supabase() {
  local project_dir="$1"

  local dev_dirs=(
    "dev/00-vision"
    "dev/01-architecture"
    "dev/02-supabase"
    "dev/03-app"
    "dev/04-lib"
    "dev/05-hooks"
    "dev/06-components/ui"
    "dev/06-components/layout"
    "dev/07-types"
    "dev/08-public"
  )

  for d in "${dev_dirs[@]}"; do
    mkdir -p "$project_dir/$d"
  done

  _write_readme "$project_dir/dev" \
    "Dev" \
    "Código-fonte e documentação técnica do produto."

  _write_readme "$project_dir/dev/00-vision" \
    "Visão do Produto" \
    "Briefing, escopo, requisitos e decisões estratégicas do produto."

  _write_readme "$project_dir/dev/01-architecture" \
    "Arquitetura" \
    "Diagramas, decisões técnicas (ADRs) e estrutura do sistema."

  _write_readme "$project_dir/dev/02-supabase" \
    "Supabase" \
    "Migrations, schemas, Edge Functions e políticas RLS."

  _write_readme "$project_dir/dev/03-app" \
    "App" \
    "Rotas e páginas da aplicação (Next.js App Router). Componentes específicos de rota em \`_components/\` dentro de cada rota."

  _write_readme "$project_dir/dev/04-lib" \
    "Lib" \
    "Funções utilitárias, helpers e código compartilhado entre módulos."

  _write_readme "$project_dir/dev/05-hooks" \
    "Hooks" \
    "React hooks customizados reutilizáveis."

  _write_readme "$project_dir/dev/06-components" \
    "Components" \
    "Componentes reutilizáveis da interface, organizados por tipo."

  _write_readme "$project_dir/dev/06-components/ui" \
    "UI" \
    "Componentes primitivos de UI: botões, inputs, modais, badges e similares."

  _write_readme "$project_dir/dev/06-components/layout" \
    "Layout" \
    "Componentes de estrutura e layout: header, sidebar, grid e wrappers."

  _write_readme "$project_dir/dev/07-types" \
    "Types" \
    "Definições de tipos TypeScript compartilhados entre módulos."

  _write_readme "$project_dir/dev/08-public" \
    "Public" \
    "Assets estáticos públicos: imagens, fontes e ícones."

  ok "dev/ criado (nextjs-supabase)"
}

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 3 — install-resource: instala recurso do hub
# ─────────────────────────────────────────────────────────────────────────────

cmd_install() {
  local type="${1:-}" name="${2:-}"
  [[ -n "$type" ]] || die "Tipo obrigatório: install.sh install-resource <tipo> <nome>"
  [[ -n "$name" ]] || die "Nome obrigatório: install.sh install-resource $type <nome>"

  header "Instalando $type: $name"

  local project_name
  project_name="$(get_project_name)"

  case "$type" in
    skill|agent|command) _install_md_resource "$type" "$name" "$project_name" ;;
    hook)                _install_hook "$name" "$project_name" ;;
    plugin)              _install_plugin "$name" "$project_name" ;;
    instruction)         _install_instruction "$name" ;;
    *) die "Tipo desconhecido: $type. Use: skill, agent, hook, command, plugin, instruction" ;;
  esac
}

_install_md_resource() {
  local type="$1" name="$2" project_name="$3"

  local src dest_dir dest
  src="$(hub_main_file "$type" "$name")"
  dest_dir="$(dest_dir_for_type "$type" "$DEST_DIR")"
  dest="$dest_dir/$name.md"

  [[ -f "$src" ]] || die "Recurso não encontrado: $src"

  local version
  version="$(get_frontmatter_field "$src" "version" 2>/dev/null || echo "0.0.0")"

  local tmp
  tmp="$(mktemp)"
  trap "rm -f '$tmp'" EXIT
  cp "$src" "$tmp"
  util_inject_frontmatter "$tmp" "$project_name" "hub/${type}s/$name@$version"
  if util_copy_versioned "$tmp" "$dest" "$name" "$version"; then
    [[ "$DRY_RUN" != true ]] && ok "Instalado: $dest"
  fi
  rm -f "$tmp"
  trap - EXIT
}

_install_hook() {
  local name="$1" project_name="$2"

  local hook_dir="$SCRIPT_DIR/hub/hooks/$name"
  local hook_json="$hook_dir/hook.json"
  local hook_sh="$hook_dir/hook.sh"

  [[ -d "$hook_dir" ]]  || die "Hook não encontrado: $hook_dir"
  [[ -f "$hook_json" ]] || die "hook.json ausente: $hook_json"
  [[ -f "$hook_sh" ]]   || die "hook.sh ausente: $hook_sh"

  local version
  version="$(get_json_field "$hook_json" "version")"

  local dest_dir="$DEST_DIR/hooks/$name"

  local v_installed=""
  if [[ -f "$dest_dir/hook.json" ]]; then
    v_installed="$(get_json_field "$dest_dir/hook.json" "version" || echo "?")"

    if [[ "$DRY_RUN" == true ]]; then
      info "[dry-run] hook $name já instalado (atual: $v_installed, novo: $version) — seria sobrescrito"
      return 0
    fi

    printf '\n  Hook %s já instalado (atual: %s, novo: %s).\n' "$name" "$v_installed" "$version"
    printf '  [s] sobrescrever  [p] pular  [c] cancelar: '
    read -r choice
    case "$choice" in
      [Ss]) : ;;
      [Pp]) info "Pulando $name"; return 0 ;;
      *) die "Cancelado." ;;
    esac
  elif [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] $hook_dir/ -> $dest_dir/"
    return 0
  fi

  mkdir -p "$dest_dir"

  local tmp_json
  tmp_json="$(mktemp)"
  python3 - "$hook_json" "$tmp_json" "$project_name" "hub/hooks/$name@$version" "$TODAY" <<'EOF'
import json, sys
src, dst, project, source, today = sys.argv[1:6]
with open(src) as f:
    data = json.load(f)
data['project'] = project
data['source'] = source
data['created'] = today
with open(dst, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF
  cp "$tmp_json" "$dest_dir/hook.json"
  rm -f "$tmp_json"

  cp "$hook_sh" "$dest_dir/hook.sh"
  chmod +x "$dest_dir/hook.sh"
  ok "Hook instalado: $dest_dir/"

  util_edit_settings_json "$DEST_DIR/settings.json" "$name" "$dest_dir/hook.json"
}

_install_plugin() {
  local name="$1" project_name="$2"

  local plugin_json="$SCRIPT_DIR/hub/plugins/$name/plugin.json"
  [[ -f "$plugin_json" ]] || die "Plugin não encontrado: $plugin_json"

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] plugin $name — recursos que seriam instalados:"
    python3 - "$plugin_json" <<'EOF'
import json, sys
p = json.load(open(sys.argv[1]))
for s in p.get('skills',   []): print(f'    skill   {s}')
for a in p.get('agents',   []): print(f'    agent   {a}')
for h in p.get('hooks',    []): print(f'    hook    {h}')
for c in p.get('commands', []): print(f'    command {c}')
EOF
    return 0
  fi

  info "Lendo manifesto: $plugin_json"

  while IFS=' ' read -r res_type res_name; do
    [[ -n "$res_type" && -n "$res_name" ]] || continue
    cmd_install "$res_type" "$res_name"
  done < <(python3 - "$plugin_json" <<'EOF'
import json, sys
p = json.load(open(sys.argv[1]))
for s in p.get('skills',   []): print(f'skill {s}')
for a in p.get('agents',   []): print(f'agent {a}')
for h in p.get('hooks',    []): print(f'hook {h}')
for c in p.get('commands', []): print(f'command {c}')
EOF
)

  if [[ "$DRY_RUN" != true ]]; then
    local version
    version="$(get_json_field "$plugin_json" "version")"
    echo "{\"name\":\"$name\",\"version\":\"$version\",\"installed\":\"$TODAY\"}" \
      > "$DEST_DIR/plugins/$name.json"
    ok "Plugin registrado: .claude/plugins/$name.json"
  fi
}

_install_instruction() {
  local name="$1"

  local src="$SCRIPT_DIR/hub/instructions/$name.md"
  local dest_claude="$DEST_DIR/CLAUDE.md"

  [[ -f "$src" ]] || die "Instruction não encontrada: $src"
  [[ -f "$dest_claude" ]] || die "CLAUDE.md não encontrado — execute /setup-claude primeiro"

  local marker="<!-- instruction: $name -->"
  if grep -qF "$marker" "$dest_claude" 2>/dev/null; then
    info "Instruction '$name' já presente em CLAUDE.md — mantida"
    return 0
  fi

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] colaria $src em $dest_claude"
    return 0
  fi

  python3 - "$src" "$dest_claude" "$marker" <<'EOF'
import re, sys
src, dest, marker = sys.argv[1:4]
content = open(src).read()
m = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
fragment = content[m.end():] if m else content
with open(dest, 'a') as f:
    f.write(f'\n{marker}\n' + fragment.strip() + '\n')
EOF

  ok "Instruction '$name' adicionada ao CLAUDE.md"
}

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 4 — build-resource: cria recurso a partir do template
# ─────────────────────────────────────────────────────────────────────────────

cmd_new() {
  local type="${1:-}" name="${2:-}"
  [[ -n "$type" ]] || die "Tipo obrigatório: install.sh build-resource <tipo> <nome>"
  [[ -n "$name" ]] || die "Nome obrigatório: install.sh build-resource $type <nome>"

  header "Criando $type: $name"

  local project_name
  project_name="$(get_project_name)"

  if [[ "$type" == "hook" ]]; then
    _new_hook "$name" "$project_name"
    return 0
  fi

  local tmpl_dir dest_dir dest
  tmpl_dir="$(template_dir_for_type "$type")"
  dest_dir="$(dest_dir_for_type "$type" "$DEST_DIR")"

  local tmpl_file
  case "$type" in
    skill)   tmpl_file="$tmpl_dir/skill.md" ;;
    agent)   tmpl_file="$tmpl_dir/agent.md" ;;
    command) tmpl_file="$tmpl_dir/command-name.md" ;;
    plugin)  tmpl_file="$tmpl_dir/plugin.json" ;;
  esac

  dest="$dest_dir/$name.md"
  [[ "$type" == "plugin" ]] && dest="$dest_dir/$name.json"

  [[ -f "$tmpl_file" ]] || die "Template não encontrado: $tmpl_file"

  if [[ -f "$dest" ]]; then
    die "Recurso já existe: $dest — edite-o diretamente ou use /publish-resource para publicá-lo"
  fi

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] $tmpl_file -> $dest"
    return 0
  fi

  mkdir -p "$dest_dir"
  cp "$tmpl_file" "$dest"

  python3 - "$dest" "$name" "$project_name" "$TODAY" <<'EOF'
import re, sys, json as json_mod
file, name, project, today = sys.argv[1:5]
content = open(file).read()

if file.endswith('.json'):
    data = json_mod.loads(content)
    if data.get('name') == 'plugin-name':
        data['name'] = name
    data['project'] = project
    data['created'] = today
    data['source'] = 'local'
    open(file, 'w').write(json_mod.dumps(data, indent=2, ensure_ascii=False) + '\n')
else:
    def set_field(text, key, value):
        pattern = rf'^{re.escape(key)}:.*$'
        repl = f'{key}: {value}'
        if re.search(pattern, text, re.MULTILINE):
            return re.sub(pattern, repl, text, flags=re.MULTILINE)
        return text

    for placeholder in ['skill-name', 'agent-name', 'command-name']:
        content = content.replace(placeholder, name)

    content = set_field(content, 'name', name)
    content = set_field(content, 'created', today)
    content = set_field(content, 'project', project)
    content = set_field(content, 'source', 'local')

    open(file, 'w').write(content)
EOF

  ok "Criado: $dest"
  info "Preencha os placeholders e use /publish-resource quando estiver pronto"
}

_new_hook() {
  local name="$1" project_name="$2"

  local tmpl_dir="$SCRIPT_DIR/build/02-hooks/_template"
  local dest_dir="$DEST_DIR/hooks/$name"

  if [[ -d "$dest_dir" ]]; then
    die "Hook já existe: $dest_dir — edite-o diretamente ou use /publish-resource para publicá-lo"
  fi

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] criaria $dest_dir/hook.json e hook.sh"
    return 0
  fi

  mkdir -p "$dest_dir"
  cp "$tmpl_dir/hook.json"               "$dest_dir/hook.json"
  cp "$tmpl_dir/events/pre-tool-use.sh"  "$dest_dir/hook.sh"
  chmod +x "$dest_dir/hook.sh"

  python3 - "$dest_dir/hook.json" "$name" "$project_name" "$TODAY" <<'EOF'
import json, sys
file, name, project, today = sys.argv[1:5]
with open(file) as f:
    data = json.load(f)
data['name'] = name
data['project'] = project
data['created'] = today
data['source'] = 'local'
with open(file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF

  ok "Criado: $dest_dir/"
  info "Edite hook.json (evento, matcher) e hook.sh (lógica)."
  info "Use /publish-resource hook $name quando estiver pronto."
}

# ─────────────────────────────────────────────────────────────────────────────
# Etapa 5 — publish-resource: normaliza e publica recurso no hub
# ─────────────────────────────────────────────────────────────────────────────

cmd_publish() {
  local type="${1:-}" name="${2:-}"
  [[ -n "$type" ]] || die "Tipo obrigatório: install.sh publish-resource <tipo> <nome>"
  [[ -n "$name" ]] || die "Nome obrigatório: install.sh publish-resource $type <nome>"

  header "Publicando $type: $name"

  [[ "$type" == "hook" ]] && { _publish_hook "$name"; return 0; }

  if [[ "$type" == "plugin" ]]; then
    die "Publicação de plugin não suportada via publish-resource. Edite hub/plugins/$name/plugin.json diretamente."
  fi

  local src_dir src
  src_dir="$(dest_dir_for_type "$type" "$DEST_DIR")"
  src="$src_dir/$name.md"

  [[ -f "$src" ]] || die "Recurso não encontrado: $src"

  util_validate_for_publish "$src"

  local version description tags project_name
  version="$(get_frontmatter_field "$src" "version" 2>/dev/null || echo "1.0.0")"
  description="$(get_frontmatter_field "$src" "description" 2>/dev/null || echo "")"
  tags="$(get_frontmatter_field "$src" "tags" 2>/dev/null || echo "[]")"
  project_name="$(get_frontmatter_field "$src" "project" 2>/dev/null || echo "")"

  local hub_dir hub_file
  hub_dir="$SCRIPT_DIR/hub/${type}s/$name"
  hub_file="$hub_dir/${type}.md"

  if [[ -f "$hub_file" ]]; then
    local bumped
    bumped="$(util_bump_version "$version")"
    info "Recurso já existe no hub — bump de versão: $version -> $bumped"
    version="$bumped"
  fi

  local tmp
  tmp="$(mktemp)"
  cp "$src" "$tmp"
  util_set_frontmatter_field "$tmp" "version" "$version"
  util_set_frontmatter_field "$tmp" "updated" "$TODAY"
  util_strip_frontmatter "$tmp"
  util_normalize_body "$tmp" "$project_name"

  header "Diff do que será publicado:"
  if [[ -f "$hub_file" ]]; then
    diff "$hub_file" "$tmp" || true
  else
    cat "$tmp"
  fi
  echo ""

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] publicaria $hub_file"
    rm -f "$tmp"
    return 0
  fi

  if ! confirm "Publicar $name@$version no hub?"; then
    rm -f "$tmp"
    die "Publicação cancelada."
  fi

  util_set_frontmatter_field "$src" "version" "$version"

  mkdir -p "$hub_dir"
  cp "$tmp" "$hub_file"
  rm -f "$tmp"
  ok "Publicado: $hub_file"

  util_update_registry "$type" "$name" "$version" "$description" "$tags"
  append_changelog "$type" "$name" "$version"

  ok "$name@$version disponível no hub"
}

_publish_hook() {
  local name="$1"

  local src_dir="$DEST_DIR/hooks/$name"
  local hook_json="$src_dir/hook.json"
  local hook_sh="$src_dir/hook.sh"

  [[ -d "$src_dir" ]]   || die "Hook não encontrado: $src_dir"
  [[ -f "$hook_json" ]] || die "hook.json ausente: $hook_json"
  [[ -f "$hook_sh" ]]   || die "hook.sh ausente: $hook_sh"

  local version description tags
  version="$(get_json_field "$hook_json" "version")"
  description="$(get_json_field "$hook_json" "description")"
  tags="$(get_json_field "$hook_json" "tags" || echo "[]")"

  if [[ -z "$description" || "$description" == '""' || "$description" == "(preencher)" ]]; then
    die "Campo obrigatório ausente: description — preencha hook.json antes de publicar"
  fi

  local hub_dir="$SCRIPT_DIR/hub/hooks/$name"
  local hub_json="$hub_dir/hook.json"

  if [[ -d "$hub_dir" ]]; then
    local bumped
    bumped="$(util_bump_version "$version")"
    info "Hook já existe no hub — bump de versão: $version -> $bumped"
    version="$bumped"
  fi

  local tmp_json
  tmp_json="$(mktemp)"
  python3 - "$hook_json" "$tmp_json" "$version" "$TODAY" <<'EOF'
import json, sys
src, dst, version, today = sys.argv[1:5]
with open(src) as f:
    data = json.load(f)
data['version'] = version
data['updated'] = today
data['scope'] = 'global'
data.pop('project', None)
data.pop('source', None)
with open(dst, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF

  header "Diff do que será publicado (hook.json):"
  if [[ -f "$hub_json" ]]; then
    diff "$hub_json" "$tmp_json" || true
  else
    cat "$tmp_json"
  fi
  echo ""

  if [[ "$DRY_RUN" == true ]]; then
    info "[dry-run] publicaria $hub_dir/"
    rm -f "$tmp_json"
    return 0
  fi

  if ! confirm "Publicar hook $name@$version no hub?"; then
    rm -f "$tmp_json"
    die "Publicação cancelada."
  fi

  python3 - "$hook_json" "$version" <<'EOF'
import json, sys
file, version = sys.argv[1:3]
with open(file) as f:
    data = json.load(f)
data['version'] = version
with open(file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
EOF

  mkdir -p "$hub_dir"
  cp "$tmp_json" "$hub_json"
  cp "$hook_sh"  "$hub_dir/hook.sh"
  rm -f "$tmp_json"
  ok "Publicado: $hub_dir/"

  util_update_registry "hook" "$name" "$version" "$description" "$tags"
  append_changelog "hook" "$name" "$version"

  ok "$name@$version disponível no hub"
}

# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

usage() {
  cat <<EOF

Uso: install.sh <comando> [tipo] [nome] [flags]

Comandos:
  claude-start                       Setup global da máquina (~/.claude/)
  setup-claude <nome>                Configura novo projeto (.claude/)
  install-resource <tipo> <nome>     Instala recurso do hub no projeto
  build-resource <tipo> <nome>       Cria recurso a partir do template
  publish-resource <tipo> <nome>     Publica recurso no hub

Tipos:
  skill, agent, hook, command, plugin, instruction

Flags:
  --global      Opera em ~/.claude/ em vez de .claude/
  --dry-run     Exibe o que seria feito sem executar

EOF
}

main() {
  local cmd="${1:-}"
  shift || true

  local args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) DRY_RUN=true ;;
      --global)  GLOBAL=true ;;
      *) args+=("$1") ;;
    esac
    shift
  done

  if [[ "$GLOBAL" == true ]]; then
    DEST_DIR="$HOME/.claude"
  else
    DEST_DIR="$PWD/.claude"
  fi

  [[ "$DRY_RUN" == true ]] && info "Modo dry-run ativo — nenhuma alteração será feita"

  case "$cmd" in
    claude-start)      cmd_init ;;
    setup-claude)      cmd_init_project "${args[0]:-}" ;;
    install-resource)  cmd_install "${args[0]:-}" "${args[1]:-}" ;;
    build-resource)    cmd_new "${args[0]:-}" "${args[1]:-}" ;;
    publish-resource)  cmd_publish "${args[0]:-}" "${args[1]:-}" ;;
    help|--help|-h)    usage ;;
    "") usage; exit 1 ;;
    *) die "Comando desconhecido: '$cmd'. Use 'install.sh help' para ver os comandos." ;;
  esac
}

main "$@"
