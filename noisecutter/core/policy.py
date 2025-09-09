from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class PolicyLevel(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class FailOn(str, Enum):
    reachable = "reachable"
    all = "all"
    none = "none"


_ORDER = {
    PolicyLevel.info: 0,
    PolicyLevel.low: 1,
    PolicyLevel.medium: 2,
    PolicyLevel.high: 3,
    PolicyLevel.critical: 4,
}


def _level_to_order(level: str) -> int:
    mapping = {"note": 0, "warning": 2, "error": 3}
    return mapping.get(level, 0)


def evaluate_policy(
    sarif_path: Path,
    min_level: PolicyLevel,
    fail_on: FailOn,
) -> List[Dict[str, Any]]:
    sarif = json.loads(sarif_path.read_text())
    results = sarif.get("runs", [{}])[0].get("results", [])

    min_order = _ORDER[min_level]
    violations: List[Dict[str, Any]] = []
    for r in results:
        level = r.get("level", "note")  # noqa: F841
        props = r.get("properties", {})
        sev = (props.get("severity") or "LOW").upper()
        sev_order_domain = {
            "INFO": 0,
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }
        if sev_order_domain.get(sev, 0) < min_order:
            continue
        if fail_on == FailOn.none:
            continue
        if fail_on == FailOn.reachable and not props.get("reachable", False):
            continue
        violations.append(r)
    return violations
