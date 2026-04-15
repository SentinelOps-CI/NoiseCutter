from __future__ import annotations

import json
from pathlib import Path

import pytest

from noisecutter.utils import write_json_deterministic


def test_write_json_deterministic_strict_sorts_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NOISECUTTER_STRICT_REPRO", "1")
    p = tmp_path / "out.json"
    write_json_deterministic(p, {"z": 1, "a": {"b": 2}})
    text = p.read_text(encoding="utf-8")
    data = json.loads(text)
    assert list(data.keys()) == ["a", "z"]
    assert "\n" not in text or text.count("\n") <= 1
