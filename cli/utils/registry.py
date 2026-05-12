from pathlib import Path


def load(hub_dir: Path) -> dict:
    raise NotImplementedError("registry.load: implementação pendente (Fase 1)")


def save(hub_dir: Path, data: dict) -> None:
    raise NotImplementedError("registry.save: implementação pendente (Fase 1)")


def find(hub_dir: Path, resource_type: str, name: str) -> dict | None:
    raise NotImplementedError("registry.find: implementação pendente (Fase 1)")


def upsert(hub_dir: Path, resource_type: str, name: str, metadata: dict) -> None:
    raise NotImplementedError("registry.upsert: implementação pendente (Fase 1)")
