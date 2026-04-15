from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

from ..cache import Cache
from ..logging_utils import get_logger

_log = get_logger(__name__)


def _ensure_syft() -> str:
    env_path = os.environ.get("SYFT_EXE")
    if env_path and Path(env_path).exists():
        return env_path
    exe = shutil.which("syft")
    if exe:
        return exe
    local_bin = Path.cwd() / "bin"
    for name in ("syft", "syft.exe"):
        candidate = local_bin / name
        if candidate.exists():
            return str(candidate)
    raise RuntimeError(
        "syft not found. Install from https://github.com/anchore/syft "
        "or set SYFT_EXE to the syft binary path."
    )


def _syft_version(syft_path: str) -> str:
    try:
        proc = subprocess.run(
            [syft_path, "version", "-o", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = cast(dict[str, Any], json.loads(proc.stdout))
        ver_block = data.get("version")
        inner = ver_block if isinstance(ver_block, dict) else {}
        return str(inner.get("version", "unknown"))
    except Exception:
        try:
            proc = subprocess.run(
                [syft_path, "version"],
                check=True,
                capture_output=True,
                text=True,
            )
            line = proc.stdout.strip().splitlines()[0]
            return line.split()[-1]
        except Exception:
            return "unknown"


def _git_sha_for_path(path: Path) -> str:
    # Try to get git HEAD sha for deterministic cache key
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(path if path.is_dir() else path.parent),
        )
        return proc.stdout.strip()
    except Exception:
        return "nogit"


def generate_sbom(
    source_path: Path | None,
    image_ref: str | None,
    cache: Cache | None = None,
) -> dict[str, Any]:
    syft = _ensure_syft()
    target = None
    if image_ref:
        target = f"registry:{image_ref}"
    elif source_path:
        target = str(source_path)
    else:
        raise ValueError("Either source or image must be provided")
    syft_ver = _syft_version(syft)
    git_sha = _git_sha_for_path(Path(target) if source_path else Path.cwd())
    cache_key = f"sbom:{target}@syft:{syft_ver}@git:{git_sha}"
    if cache is not None:
        doc = cache.get_json(cache_key)
        if doc is not None:
            _log.debug("syft cache hit for %s", target)
            return doc
    cmd = [
        syft,
        target,
        "-o",
        "cyclonedx-json",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    doc = cast(dict[str, Any], json.loads(proc.stdout))
    # Normalize timestamp for reproducibility if SOURCE_DATE_EPOCH is set
    try:
        import datetime as _dt
        import os

        epoch = os.environ.get("SOURCE_DATE_EPOCH")
        if epoch:
            ts = _dt.datetime.utcfromtimestamp(int(epoch)).strftime("%Y-%m-%dT%H:%M:%SZ")
            meta = doc.setdefault("metadata", {})
            meta["timestamp"] = ts
    except Exception:
        pass
    if cache is not None:
        cache.set_json(cache_key, doc)
    return doc
