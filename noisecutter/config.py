from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class SBOMConfig(BaseModel):
    tool: str = Field(default="syft")
    args: List[str] = Field(default_factory=list)


class AuditConfig(BaseModel):
    tool: str = Field(default="osv")
    args: List[str] = Field(default_factory=list)


class ReachConfig(BaseModel):
    lang: str = Field(default="go")
    entry: List[str] = Field(default_factory=list)
    tool: str = Field(default="govulncheck")


class FuseConfig(BaseModel):
    out: str = Field(default="report.sarif")


class PolicyConfig(BaseModel):
    level: str = Field(default="high")
    fail_on: str = Field(default="reachable")
    max_total_findings: Optional[int] = None
    max_reachable_findings: Optional[int] = None
    exclude_rules: List[str] = Field(default_factory=list)
    exclude_modules: List[str] = Field(default_factory=list)
    only_levels: List[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    sbom: SBOMConfig = Field(default_factory=SBOMConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    reach: ReachConfig = Field(default_factory=ReachConfig)
    fuse: FuseConfig = Field(default_factory=FuseConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    cache_dir: str = Field(default=".noisecutter-cache")
    concurrency: int = Field(default=4)
    timeout_sec: int = Field(default=300)
    strict_repro: bool = Field(default=False)


def _default_config_path(start_dir: Path) -> Path:
    return start_dir / ".noisecutter.yaml"


def load_config(repo_root: Optional[Path] = None) -> AppConfig:
    root = repo_root or Path.cwd()
    cfg_path = _default_config_path(root)
    data: Dict[str, Any] = {}
    if cfg_path.exists():
        # Use safe loader, assume UTF-8
        text = cfg_path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(text) or {}
        if not isinstance(parsed, dict):
            raise ValueError(".noisecutter.yaml must be a mapping")
        data = parsed
    cfg = AppConfig.model_validate(data)

    # Environment overrides
    strict_repro_env = os.environ.get("NOISECUTTER_STRICT_REPRO")
    if strict_repro_env is not None:
        cfg.strict_repro = strict_repro_env.lower() in {"1", "true", "yes"}
    concurrency_env = os.environ.get("NOISECUTTER_CONCURRENCY")
    if concurrency_env and concurrency_env.isdigit():
        cfg.concurrency = int(concurrency_env)
    cache_dir_env = os.environ.get("NOISECUTTER_CACHE_DIR")
    if cache_dir_env:
        cfg.cache_dir = cache_dir_env
    timeout_env = os.environ.get("NOISECUTTER_TIMEOUT_SEC")
    if timeout_env and timeout_env.isdigit():
        cfg.timeout_sec = int(timeout_env)
    return cfg
