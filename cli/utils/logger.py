import json
from datetime import datetime
from pathlib import Path

from cli.utils.files import git_author


def log(dest_dir: Path, event: str, data: dict) -> None:
    entry = {
        "ts":    datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "event": event,
        "actor": git_author(),
        "data":  data,
    }
    log_file = dest_dir / "project.log"
    try:
        with log_file.open("a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass
