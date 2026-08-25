"""Safe JSON persistence: atomic writes plus rolling backups.

Every save writes to a temp file and renames it over the target (atomic on
POSIX and Windows), so a crash or interrupt mid-write can never leave a
truncated or partially-written data file behind. Before overwriting, the
previous version is copied into data/.backups/ so a bad edit can be
recovered by hand.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
BACKUP_DIR = DATA_DIR / ".backups"
MAX_BACKUPS_PER_FILE = 10


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


_backup_counter = 0


def _rotate_backups(path: Path) -> None:
    if not path.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    global _backup_counter
    _backup_counter += 1
    stamp = f"{time.strftime('%Y%m%dT%H%M%S')}-{_backup_counter:06d}"
    backup_path = BACKUP_DIR / f"{path.stem}.{stamp}.bak.json"
    shutil.copy2(path, backup_path)

    existing = sorted(BACKUP_DIR.glob(f"{path.stem}.*.bak.json"))
    for stale in existing[:-MAX_BACKUPS_PER_FILE]:
        stale.unlink(missing_ok=True)


def save_json(path: Path, data: Any) -> None:
    """Back up the current file (if any), then atomically overwrite it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _rotate_backups(path)

    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


class ValidationError(ValueError):
    """Raised when data fails structural validation before being saved."""
