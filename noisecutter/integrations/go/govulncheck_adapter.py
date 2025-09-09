from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...cache import Cache
from ...logging_utils import get_logger

_log = get_logger(__name__)


def _ensure_govulncheck() -> str:
    exe = shutil.which("govulncheck")
    if not exe:
        raise RuntimeError(
            "govulncheck not found. Install via `go install "
            "golang.org/x/vuln/cmd/govulncheck@latest`"
        )
    return exe


def _find_go_module_root(start_path: Path) -> Optional[Path]:
    path = start_path.resolve()
    cursor = path if path.is_dir() else path.parent
    while True:
        if (cursor / "go.mod").exists():
            return cursor
        if cursor.parent == cursor:
            return None
        cursor = cursor.parent


def _run_govulncheck(entry_path: Path) -> Dict[str, Any]:
    exe = _ensure_govulncheck()
    module_root = _find_go_module_root(entry_path)
    if module_root is None:
        raise RuntimeError(
            f"No go.mod found for entry path {entry_path}. "
            "Run from a Go module or point to a path under a module."
        )
    try:
        rel = entry_path.resolve().relative_to(module_root)
    except ValueError:
        rel = Path(".")
    rel_str = rel.as_posix()
    # Ensure Go treats it as a relative package pattern, not an import path
    if rel_str != "." and not rel_str.startswith("./"):
        rel_str = f"./{rel_str}"
    cmd = [exe, "-mode=source", "-json", rel_str]
    try:
        proc = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(module_root),
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else ""
        raise RuntimeError(f"govulncheck failed: {stderr}") from e
    # govulncheck outputs JSON lines; collect findings
    records: List[Dict[str, Any]] = []
    stdout_text = proc.stdout or ""
    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("Finding"):
            records.append(obj)
    return {"findings": records}


def compute_reachability_go(
    entry_path: Path,
    vulns_json: Path,
    coverage_path: Optional[Path],
    cache: Optional[Cache] = None,
) -> Dict[str, Any]:
    cache_key = f"govulncheck:{entry_path.resolve().as_posix()}"
    findings: Optional[Dict[str, Any]] = None
    if cache is not None:
        cached = cache.get_json(cache_key)
        if cached is not None:
            _log.debug("govulncheck cache hit %s", cache_key)
            findings = cached
    if findings is None:
        findings = _run_govulncheck(entry_path)
        if cache is not None:
            cache.set_json(cache_key, findings)
    by_id: Dict[str, Dict[str, Any]] = {}
    for f in (findings or {}).get("findings", []):
        vuln = (f.get("Finding") or {}).get("Vuln") or {}
        vuln_id = vuln.get("ID")
        if not vuln_id:
            continue
        call_stack = []
        for fr in (f.get("Finding") or {}).get("Trace", []):
            fn = fr.get("Function") or {}
            name = fn.get("Name")
            if name:
                call_stack.append(name)
        rec = by_id.setdefault(
            vuln_id,
            {"id": vuln_id, "reachable": True, "callPaths": []},
        )
        if call_stack:
            rec["callPaths"].append(call_stack)

    coverage_evidence: Dict[str, Any] = {}
    if coverage_path and coverage_path.exists():
        coverage_evidence = {"coverageFile": str(coverage_path)}

    with open(vulns_json, "r", encoding="utf-8") as f:
        vulns_doc = json.load(f)
    out_records: List[Dict[str, Any]] = []
    for v in vulns_doc.get("vulnerabilities", []):
        vid = v.get("id") or v.get("osvId")
        base = {"id": vid, "reachable": False, "callPaths": [], "evidence": {}}
        if vid in by_id:
            base.update(by_id[vid])
            base["reachable"] = True
        if coverage_evidence:
            base.setdefault("evidence", {}).update(coverage_evidence)
        out_records.append(base)
    return {"records": out_records}
