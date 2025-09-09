from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, TypedDict, TypeAlias


class Severity(str, Enum):
    info = "INFO"
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


class ReachabilityRecord(TypedDict, total=False):
    id: str
    reachable: bool
    callPaths: List[List[str]]
    evidence: Dict[str, Any]


SarifResult: TypeAlias = Dict[str, Any]
SarifLog: TypeAlias = Dict[str, Any]
