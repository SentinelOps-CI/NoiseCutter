from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _stable_json_dumps(data: Any) -> str:
    # Deterministic JSON with optional pretty when not strict
    strict = os.environ.get("NOISECUTTER_STRICT_REPRO")
    indent_val = None if strict else 2
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        indent=indent_val,
    )


def write_json_deterministic(path: Path, data: dict[str, Any]) -> None:
    text = _stable_json_dumps(data)
    path.write_bytes(text.encode("utf-8"))
