from __future__ import annotations

import json
from pathlib import Path

from noisecutter.core.fuse import fuse_to_sarif

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_GOLDEN = Path(__file__).resolve().parent / "golden"


def test_fuse_matches_golden_minimal() -> None:
    expected = json.loads((_GOLDEN / "expected_fuse_minimal.json").read_text(encoding="utf-8"))
    actual = fuse_to_sarif(
        _FIXTURES / "minimal_sbom.json",
        _FIXTURES / "minimal_vulns.json",
        _FIXTURES / "minimal_reach.json",
    )
    assert actual == expected
