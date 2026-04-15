from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import respx

from noisecutter.integrations.osv_adapter import audit_osv


@respx.mock
def test_audit_osv_retries_on_503(tmp_path: Path) -> None:
    with patch("noisecutter.integrations.osv_adapter.time.sleep"):
        route = respx.post("https://api.osv.dev/v1/query").mock(
            side_effect=[
                httpx.Response(503),
                httpx.Response(200, json={"vulns": []}),
            ]
        )
        sbom = tmp_path / "sbom.json"
        sbom.write_text(
            json.dumps(
                {
                    "components": [
                        {
                            "type": "library",
                            "name": "left-pad",
                            "version": "1.0.0",
                            "purl": "pkg:npm/left-pad@1.0.0",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        out = audit_osv(sbom)
        assert out == {"vulnerabilities": []}
        assert route.call_count == 2


@respx.mock
def test_audit_osv_posts_expected_payload(tmp_path: Path) -> None:
    captured: list[dict[str, object]] = []

    def _handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(200, json={"vulns": []})

    respx.post("https://api.osv.dev/v1/query").mock(side_effect=_handler)
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "components": [
                    {
                        "type": "library",
                        "name": "acme",
                        "version": "2.0.0",
                        "purl": "pkg:pypi/acme@2.0.0",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    audit_osv(sbom)
    assert len(captured) == 1
    assert captured[0]["version"] == "2.0.0"
    assert captured[0]["package"]["name"] == "acme"
    assert "ecosystem" not in captured[0]["package"]


@respx.mock
def test_audit_osv_maps_severity_from_cvss(tmp_path: Path) -> None:
    respx.post("https://api.osv.dev/v1/query").mock(
        return_value=httpx.Response(
            200,
            json={
                "vulns": [
                    {
                        "id": "OSV-1",
                        "severity": [{"type": "CVSS_V3", "score": "8.1"}],
                    }
                ]
            },
        )
    )
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "components": [
                    {"type": "library", "name": "x", "version": "1", "purl": "pkg:npm/x@1"}
                ]
            }
        ),
        encoding="utf-8",
    )
    out = audit_osv(sbom)
    assert out["vulnerabilities"][0]["severity"] == "HIGH"
    assert out["vulnerabilities"][0]["id"] == "OSV-1"
