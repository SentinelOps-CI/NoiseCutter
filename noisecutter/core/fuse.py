from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .types import SarifLog, SarifResult


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _severity_to_level(sev: str) -> str:
    s = sev.upper()
    if s in {"CRITICAL", "HIGH"}:
        return "error"
    if s in {"MEDIUM"}:
        return "warning"
    return "note"


def _make_code_flows(call_paths: List[List[str]]) -> List[Dict[str, Any]]:
    flows: List[Dict[str, Any]] = []
    if not call_paths:
        return flows
    for path in call_paths:
        thread_flow = {
            "locations": [{"location": {"message": {"text": fn_name}}} for fn_name in path]
        }
        flows.append({"threadFlows": [thread_flow]})
    return flows


def fuse_to_sarif(
    sbom_path: Path,
    vulns_path: Path,
    reach_path: Path,
) -> SarifLog:
    sbom = _read_json(sbom_path)
    vulns = _read_json(vulns_path)
    reach = _read_json(reach_path)

    reach_map = {r.get("id"): r for r in reach.get("records", [])}

    results: List[SarifResult] = []
    for v in vulns.get("vulnerabilities", []):
        vuln_id = v.get("id") or v.get("cve") or v.get("osvId")
        severity = (v.get("severity") or "LOW").upper()
        pkg = v.get("package") or {}
        name = pkg.get("name")
        version = pkg.get("version")
        purl = pkg.get("purl")
        reach_rec = reach_map.get(vuln_id, {})
        reachable = bool(reach_rec.get("reachable", False))
        call_paths = reach_rec.get("callPaths") or []
        evidence = reach_rec.get("evidence") or {}

        result: SarifResult = {
            "ruleId": vuln_id or "UNKNOWN",
            "level": _severity_to_level(severity),
            "message": {"text": f"{vuln_id} in {name}@{version}"},
            "locations": [],
            "properties": {
                "severity": severity,
                "package": name,
                "version": version,
                "reachable": reachable,
                "callPaths": call_paths,
                "evidence": evidence,
                "tool": {
                    "sbom": sbom.get("metadata", {}).get("tools", []),
                },
            },
        }
        # SARIF enrichments
        if purl:
            result.setdefault("partialFingerprints", {}).update(
                {
                    "purl": purl,
                    "vulnId": vuln_id or "UNKNOWN",
                }
            )
        if vuln_id and vuln_id.startswith("OSV-"):
            result.setdefault(
                "helpUri",
                f"https://osv.dev/vulnerability/{vuln_id}",
            )
        code_flows = _make_code_flows(call_paths)
        if code_flows:
            result["codeFlows"] = code_flows
        results.append(result)

    sarif: SarifLog = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "NoiseCutter",
                        "informationUri": ("https://github.com/your-org/noisecutter"),
                        "version": "0.1.0",
                    }
                },
                "results": results,
                "artifacts": [
                    {"location": {"uri": p.get("package", {}).get("purl", "")}}
                    for p in [
                        {"package": v.get("package", {})} for v in vulns.get("vulnerabilities", [])
                    ]
                    if p.get("package", {}).get("purl")
                ],
                "properties": {"noisecutter:versions": {"noisecutter": "0.1.0"}},
            }
        ],
    }
    return sarif


def write_summary_txt(sarif_doc: SarifLog, out_path: Path) -> None:
    rows: List[str] = []
    header = "package\tversion\tvuln\tlevel\treachable\tentrypoints\tcodeflow_count"
    rows.append(header)
    results = sarif_doc.get("runs", [{}])[0].get("results", [])
    for r in results:
        props = r.get("properties", {})
        pkg = props.get("package") or ""
        ver = props.get("version") or ""
        vuln = r.get("ruleId") or ""
        level = r.get("level") or ""
        reachable = props.get("reachable")
        entrypoints = ",".join(sorted({path[0] for path in (props.get("callPaths") or []) if path}))
        codeflows = len(r.get("codeFlows", []))
        row = f"{pkg}\t{ver}\t{vuln}\t{level}\t{reachable}" f"\t{entrypoints}\t{codeflows}"
        rows.append(row)
    out_path.write_text("\n".join(rows), encoding="utf-8")
