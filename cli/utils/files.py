from pathlib import Path


def copy_template(src: Path, dest: Path, overwrite: bool = False) -> None:
    raise NotImplementedError("files.copy_template: implementação pendente (Fase 1)")


def ensure_dir(path: Path) -> None:
    raise NotImplementedError("files.ensure_dir: implementação pendente (Fase 1)")


def checksum(file: Path) -> str:
    raise NotImplementedError("files.checksum: implementação pendente (Fase 1)")


def bump_version(version: str) -> str:
    raise NotImplementedError("files.bump_version: implementação pendente (Fase 1)")
