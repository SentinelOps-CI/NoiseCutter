from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def _ensure_cache_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    return base


def _key_to_path(base: Path, key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return base / f"{digest}.json"


class Cache:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = _ensure_cache_dir(base_dir)

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        p = _key_to_path(self.base_dir, key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def set_json(self, key: str, value: Dict[str, Any]) -> None:
        p = _key_to_path(self.base_dir, key)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(value, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(tmp, p)

    def stats(self) -> Dict[str, Any]:
        files = list(self.base_dir.glob("*.json"))
        size = sum(f.stat().st_size for f in files)
        return {"entries": len(files), "bytes": size}

    def clear(self) -> None:
        for f in self.base_dir.glob("*.json"):
            try:
                f.unlink()
            except Exception:
                pass
