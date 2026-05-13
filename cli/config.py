from pathlib import Path

HUB_PATH_FILE = Path.home() / ".claude" / "hub-path"


def hub_dir() -> Path:
    if not HUB_PATH_FILE.exists():
        raise RuntimeError("~/.claude/hub-path não encontrado. Execute /claude-start primeiro.")
    return Path(HUB_PATH_FILE.read_text().strip())


def dest_dir_for_type(base: Path, resource_type: str) -> Path:
    mapping = {
        "skill": base / "skills",
        "agent": base / "agents",
        "hook": base / "hooks",
        "command": base / "commands",
        "plugin": base / "plugins",
    }
    if resource_type not in mapping:
        raise ValueError(f"Tipo inválido: {resource_type}. Válidos: {', '.join(mapping)}")
    return mapping[resource_type]
