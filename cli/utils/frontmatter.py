from pathlib import Path


def read(file: Path) -> dict:
    raise NotImplementedError("frontmatter.read: implementação pendente (Fase 1)")


def write(file: Path, fields: dict) -> None:
    raise NotImplementedError("frontmatter.write: implementação pendente (Fase 1)")


def strip(file: Path, fields: list) -> None:
    raise NotImplementedError("frontmatter.strip: implementação pendente (Fase 1)")


def inject(file: Path, project: str, source: str) -> None:
    raise NotImplementedError("frontmatter.inject: implementação pendente (Fase 1)")
