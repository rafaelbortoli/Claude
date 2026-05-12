import json
from datetime import date
from pathlib import Path


def load(hub_dir: Path) -> dict:
    registry_file = hub_dir / "registry.json"
    with open(registry_file) as f:
        return json.load(f)


def save(hub_dir: Path, data: dict) -> None:
    registry_file = hub_dir / "registry.json"
    with open(registry_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


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
