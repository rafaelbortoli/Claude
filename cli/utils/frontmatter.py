import re
from datetime import date
from pathlib import Path

_FENCE = re.compile(r'^(---\n)(.*?)(\n---)', re.DOTALL)


def read(file: Path) -> dict:
    m = _FENCE.match(file.read_text())
    if not m:
        return {}
    result = {}
    for line in m.group(2).splitlines():
        if ':' in line and not line.startswith('#'):
            k, _, v = line.partition(':')
            result[k.strip()] = v.strip()
    return result


def write(file: Path, fields: dict, section: str = "") -> None:
    content = file.read_text()
    m = _FENCE.match(content)
    if not m:
        return
    fm = m.group(2)
    for key, value in fields.items():
        pattern = rf'^{re.escape(key)}:.*$'
        repl = f'{key}: {value}'
        if re.search(pattern, fm, re.MULTILINE):
            fm = re.sub(pattern, repl, fm, flags=re.MULTILINE)
        elif section and f'# {section}' in fm:
            fm = re.sub(rf'(# {re.escape(section)}\n)', rf'\1{repl}\n', fm, count=1)
        else:
            fm += f'\n{key}: {value}'
    file.write_text(m.group(1) + fm + m.group(3) + content[m.end():])


def strip(file: Path, fields: list) -> None:
    content = file.read_text()
    m = _FENCE.match(content)
    if not m:
        return
    fm = m.group(2)
    for field in fields:
        fm = re.sub(rf'^{re.escape(field)}:.*\n?', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'\n{3,}', '\n\n', fm).strip()
    file.write_text(m.group(1) + fm + m.group(3) + content[m.end():])


def inject(file: Path, project: str, source: str) -> None:
    today = str(date.today())
    content = file.read_text()
    m = _FENCE.match(content)
    if not m:
        return
    fm = m.group(2)

    def set_field(text: str, key: str, value: str) -> str:
        pattern = rf'^{re.escape(key)}:.*$'
        repl = f'{key}: {value}'
        if re.search(pattern, text, re.MULTILINE):
            return re.sub(pattern, repl, text, flags=re.MULTILINE)
        if '# system' in text:
            return re.sub(r'(# system\n)', rf'\1{repl}\n', text, count=1)
        return text + f'\n{repl}'

    fm = set_field(fm, 'project', project)
    fm = set_field(fm, 'created', today)
    fm = set_field(fm, 'source', source)
    file.write_text(m.group(1) + fm + m.group(3) + content[m.end():])
