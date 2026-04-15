from __future__ import annotations

import json
from pathlib import Path

from noisecutter.core.policy import FailOn, PolicyLevel, evaluate_policy


def test_evaluate_policy_reachable_high_only(tmp_path: Path) -> None:
    sarif = {
        "runs": [
            {
                "results": [
                    {
                        "level": "error",
                        "ruleId": "V-1",
                        "properties": {"severity": "HIGH", "reachable": True},
                    },
                    {
                        "level": "error",
                        "ruleId": "V-2",
                        "properties": {"severity": "HIGH", "reachable": False},
                    },
                ]
            }
        ]
    }
    p = tmp_path / "r.sarif"
    p.write_text(json.dumps(sarif), encoding="utf-8")
    v = evaluate_policy(p, PolicyLevel.high, FailOn.reachable)
    assert len(v) == 1
    assert v[0]["ruleId"] == "V-1"


def test_evaluate_policy_fail_on_none(tmp_path: Path) -> None:
    sarif = {
        "runs": [
            {
                "results": [
                    {
                        "level": "error",
                        "properties": {"severity": "CRITICAL", "reachable": True},
                    }
                ]
            }
        ]
    }
    p = tmp_path / "r.sarif"
    p.write_text(json.dumps(sarif), encoding="utf-8")
    assert evaluate_policy(p, PolicyLevel.high, FailOn.none) == []
