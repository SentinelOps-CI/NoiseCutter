from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, cast

import httpx

from ..cache import Cache
from ..logging_utils import get_logger

_log = get_logger(__name__)

OSV_QUERY_URL = "https://api.osv.dev/v1/query"
_MAX_ATTEMPTS = 4
_BACKOFF_BASE_SEC = 0.5


def _components_from_cyclonedx(doc: dict[str, Any]) -> list[dict[str, Any]]:
    raw = doc.get("components")
    if isinstance(raw, list):
        return cast(list[dict[str, Any]], raw)
    return []


def _retryable_status(status_code: int) -> bool:
    return status_code in (429, 500, 502, 503, 504)


def _osv_post_query(
    client: httpx.Client,
    name: str,
    version: str,
    ecosystem: str | None,
) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "version": version,
        "package": {"name": name},
    }
    if ecosystem:
        payload["package"]["ecosystem"] = ecosystem

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            resp = client.post(OSV_QUERY_URL, json=payload)
            if _retryable_status(resp.status_code) and attempt < _MAX_ATTEMPTS:
                delay = _BACKOFF_BASE_SEC * (2 ** (attempt - 1))
                _log.warning(
                    "osv transient HTTP %s for %s@%s (attempt %s/%s), retry in %.2fs",
                    resp.status_code,
                    name,
                    version,
                    attempt,
                    _MAX_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)
                continue
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                return []
            vulns = data.get("vulns")
            if isinstance(vulns, list):
                return cast(list[dict[str, Any]], vulns)
            return []
        except httpx.HTTPStatusError as exc:
            if _retryable_status(exc.response.status_code) and attempt < _MAX_ATTEMPTS:
                delay = _BACKOFF_BASE_SEC * (2 ** (attempt - 1))
                _log.warning(
                    "osv HTTPStatusError %s for %s@%s (attempt %s/%s), retry in %.2fs",
                    exc.response.status_code,
                    name,
                    version,
                    attempt,
                    _MAX_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)
                continue
            raise
        except httpx.RequestError as exc:
            if attempt < _MAX_ATTEMPTS:
                delay = _BACKOFF_BASE_SEC * (2 ** (attempt - 1))
                _log.warning(
                    "osv transport error for %s@%s (attempt %s/%s): %s, retry in %.2fs",
                    name,
                    version,
                    attempt,
                    _MAX_ATTEMPTS,
                    exc,
                    delay,
                )
                time.sleep(delay)
                continue
            raise RuntimeError(
                f"OSV request failed for {name}@{version} after {_MAX_ATTEMPTS} attempts"
            ) from exc
    raise RuntimeError(f"OSV request exhausted retries for {name}@{version}")


def audit_osv(
    sbom_path: Path,
    cache: Cache | None = None,
) -> dict[str, Any]:
    doc = json.loads(sbom_path.read_text())
    vulns_out: list[dict[str, Any]] = []
    timeout = httpx.Timeout(30.0)
    with httpx.Client(timeout=timeout) as client:
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
            entries: list[dict[str, Any]] | None = None
            if cache is not None:
                cached = cache.get_json(cache_key)
                if cached is not None:
                    entries = cached.get("vulns") if isinstance(cached, dict) else None
                    if entries is not None:
                        _log.debug("osv cache hit %s", cache_key)
            if entries is None:
                entries = _osv_post_query(client, name, version, ecosystem)
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
