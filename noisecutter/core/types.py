from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict

from typing_extensions import TypeAlias


class Severity(str, Enum):
    info = "INFO"
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


class ReachabilityRecord(TypedDict, total=False):
    id: str
    reachable: bool
    callPaths: list[list[str]]
    evidence: dict[str, Any]


SarifResult: TypeAlias = dict[str, Any]
SarifLog: TypeAlias = dict[str, Any]
