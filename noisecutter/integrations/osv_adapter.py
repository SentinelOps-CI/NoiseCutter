from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from ..cache import Cache
from ..logging_utils import get_logger

_log = get_logger(__name__)


def _components_from_cyclonedx(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    return doc.get("components", [])


def _osv_query(
    name: str,
    version: str,
    ecosystem: Optional[str],
) -> List[Dict[str, Any]]:
    payload: Dict[str, Any] = {
        "version": version,
        "package": {"name": name},
    }
    if ecosystem:
        payload["package"]["ecosystem"] = ecosystem
    r = httpx.post(
        "https://api.osv.dev/v1/query",
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    vulns = data.get("vulns", [])
    return vulns


def audit_osv(
    sbom_path: Path,
    cache: Optional[Cache] = None,
) -> Dict[str, Any]:
    doc = json.loads(sbom_path.read_text())
    vulns_out: List[Dict[str, Any]] = []
    for comp in _components_from_cyclonedx(doc):
        purl = comp.get("purl")
        name = comp.get("name")
        version = comp.get("version")
        ecosystem = None
        if comp.get("type") == "library":
            pass
        if not name or not version:
            continue
        cache_key = f"osv:{name}@{version}:{ecosystem or 'unknown'}"
        entries: Optional[List[Dict[str, Any]]] = None
        if cache is not None:
            cached = cache.get_json(cache_key)
            if cached is not None:
                entries = cached.get("vulns") if isinstance(cached, dict) else None
                if entries is not None:
                    _log.debug("osv cache hit %s", cache_key)
        if entries is None:
            entries = _osv_query(name, version, ecosystem)
            if cache is not None:
                cache.set_json(cache_key, {"vulns": entries})
        for v in entries:
            vuln_id = v.get("id")
            severity = "LOW"
            severities = v.get("severity") or []
            max_score: float = -1.0
            for s in severities:
                raw = s.get("score")
                try:
                    if raw is None:
                        continue
                    val = float(raw)
                    if val > max_score:
                        max_score = val
                except (TypeError, ValueError):
                    continue
            if max_score >= 0:
                if max_score >= 9:
                    severity = "CRITICAL"
                elif max_score >= 7:
                    severity = "HIGH"
                elif max_score >= 4:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
            else:
                db_sev = (v.get("database_specific") or {}).get("severity")
                if isinstance(db_sev, str) and db_sev:
                    severity = db_sev.upper()
            vulns_out.append(
                {
                    "id": vuln_id,
                    "severity": severity,
                    "package": {
                        "name": name,
                        "version": version,
                        "purl": purl,
                    },
                }
            )
    return {"vulnerabilities": vulns_out}
