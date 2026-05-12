import hashlib
import shutil
from pathlib import Path


def copy_template(src: Path, dest: Path, overwrite: bool = False) -> None:
    if dest.exists() and not overwrite:
        raise FileExistsError(f"Arquivo já existe: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def checksum(file: Path) -> str:
    h = hashlib.sha256()
    h.update(file.read_bytes())
    return h.hexdigest()


def bump_version(version: str) -> str:
    parts = version.split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)
    return version
