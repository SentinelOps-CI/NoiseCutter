from __future__ import annotations

import json
from pathlib import Path

from noisecutter.core.fuse import fuse_to_sarif

_SBOM = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "metadata": {"tools": []},
    "components": [
        {
            "type": "library",
            "name": "libx",
            "version": "1.0.0",
            "purl": "pkg:npm/libx@1.0.0",
        }
    ],
}

_REACH = {"records": []}


def _write(tmp: Path, name: str, data: object) -> Path:
    p = tmp / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_fuse_critical_maps_to_error(tmp_path: Path) -> None:
    vulns = {
        "vulnerabilities": [
            {
                "id": "CVE-TEST-1",
                "severity": "CRITICAL",
                "package": {"name": "libx", "version": "1.0.0", "purl": "pkg:npm/libx@1.0.0"},
            }
        ]
    }
    sbom = _write(tmp_path, "sbom.json", _SBOM)
    v = _write(tmp_path, "vulns.json", vulns)
    r = _write(tmp_path, "reach.json", _REACH)
    out = fuse_to_sarif(sbom, v, r)
    assert out["runs"][0]["results"][0]["level"] == "error"


def test_fuse_medium_maps_to_warning(tmp_path: Path) -> None:
    vulns = {
        "vulnerabilities": [
            {
                "id": "CVE-TEST-2",
                "severity": "MEDIUM",
                "package": {"name": "libx", "version": "1.0.0", "purl": "pkg:npm/libx@1.0.0"},
            }
        ]
    }
    sbom = _write(tmp_path, "sbom.json", _SBOM)
    v = _write(tmp_path, "vulns.json", vulns)
    r = _write(tmp_path, "reach.json", _REACH)
    out = fuse_to_sarif(sbom, v, r)
    assert out["runs"][0]["results"][0]["level"] == "warning"


def test_fuse_low_maps_to_note(tmp_path: Path) -> None:
    vulns = {
        "vulnerabilities": [
            {
                "id": "CVE-TEST-3",
                "severity": "LOW",
                "package": {"name": "libx", "version": "1.0.0", "purl": "pkg:npm/libx@1.0.0"},
            }
        ]
    }
    sbom = _write(tmp_path, "sbom.json", _SBOM)
    v = _write(tmp_path, "vulns.json", vulns)
    r = _write(tmp_path, "reach.json", _REACH)
    out = fuse_to_sarif(sbom, v, r)
    assert out["runs"][0]["results"][0]["level"] == "note"
