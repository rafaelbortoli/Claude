import json
from datetime import date
from pathlib import Path

_TYPE_PREFIX = {
    "skill":       "sk",
    "agent":       "ag",
    "command":     "cmd",
    "hook":        "hk",
    "plugin":      "pl",
    "instruction": "ins",
}


def load(hub_dir: Path) -> dict:
    registry_file = hub_dir / "registry.json"
    with open(registry_file) as f:
        return json.load(f)


def save(hub_dir: Path, data: dict) -> None:
    registry_file = hub_dir / "registry.json"
    with open(registry_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def next_id(hub_dir: Path, resource_type: str) -> str:
    prefix = _TYPE_PREFIX.get(resource_type)
    if not prefix:
        raise ValueError(f"Tipo sem prefixo de ID: {resource_type}")
    data = load(hub_dir)
    counters = data.setdefault("id_counters", {})
    counters[resource_type] = counters.get(resource_type, 0) + 1
    data["updated"] = str(date.today())
    save(hub_dir, data)
    return f"{prefix}-{counters[resource_type]:03d}"


def find(hub_dir: Path, resource_type: str, name: str) -> dict | None:
    data = load(hub_dir)
    for item in data.get(f'{resource_type}s', []):
        if item.get('name') == name:
            return item
    return None


def upsert(hub_dir: Path, resource_type: str, name: str, metadata: dict) -> None:
    data = load(hub_dir)
    type_key = f'{resource_type}s'
    data.setdefault(type_key, [])

    entry = {'name': name, **metadata}

    for i, item in enumerate(data[type_key]):
        if item.get('name') == name:
            data[type_key][i] = entry
            break
    else:
        data[type_key].append(entry)

    data['updated'] = str(date.today())
    save(hub_dir, data)
