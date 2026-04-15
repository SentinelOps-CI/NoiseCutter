from __future__ import annotations

import json
from pathlib import Path

import pytest

from noisecutter.core.fuse import validate_sarif_structure


def test_validate_sarif_structure_accepts_minimal_golden() -> None:
    p = Path(__file__).resolve().parent / "golden" / "expected_fuse_minimal.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    validate_sarif_structure(doc)


def test_validate_sarif_structure_rejects_bad_version() -> None:
    doc = json.loads(
        (Path(__file__).resolve().parent / "golden" / "expected_fuse_minimal.json").read_text(
            encoding="utf-8"
        )
    )
    doc["version"] = "2.0.0"
    with pytest.raises(ValueError, match=r"SARIF version must be 2\.1\.0"):
        validate_sarif_structure(doc)


def test_validate_sarif_structure_rejects_missing_rule_id() -> None:
    doc = json.loads(
        (Path(__file__).resolve().parent / "golden" / "expected_fuse_minimal.json").read_text(
            encoding="utf-8"
        )
    )
    doc["runs"][0]["results"][0].pop("ruleId")
    with pytest.raises(ValueError, match="ruleId"):
        validate_sarif_structure(doc)
