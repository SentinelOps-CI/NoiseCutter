from __future__ import annotations

from pathlib import Path

import pytest

from noisecutter.config import AppConfig, load_config


def test_load_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg = load_config(None)
    assert isinstance(cfg, AppConfig)
    assert cfg.cache_dir == ".noisecutter-cache"
    assert cfg.strict_repro is False


def test_load_config_rejects_non_mapping_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".noisecutter.yaml").write_text("- not\n- a\n- mapping\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_config(None)


def test_load_config_merges_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".noisecutter.yaml").write_text(
        "cache_dir: custom-cache\nstrict_repro: true\n",
        encoding="utf-8",
    )
    cfg = load_config(None)
    assert cfg.cache_dir == "custom-cache"
    assert cfg.strict_repro is True


def test_load_config_explicit_repo_root(tmp_path: Path) -> None:
    (tmp_path / ".noisecutter.yaml").write_text("timeout_sec: 42\n", encoding="utf-8")
    cfg = load_config(tmp_path)
    assert cfg.timeout_sec == 42


def test_load_config_env_strict_repro_overrides_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".noisecutter.yaml").write_text("strict_repro: false\n", encoding="utf-8")
    monkeypatch.setenv("NOISECUTTER_STRICT_REPRO", "yes")
    cfg = load_config(None)
    assert cfg.strict_repro is True


def test_load_config_env_numeric_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NOISECUTTER_CONCURRENCY", "8")
    monkeypatch.setenv("NOISECUTTER_TIMEOUT_SEC", "120")
    monkeypatch.setenv("NOISECUTTER_CACHE_DIR", "/tmp/x")
    cfg = load_config(None)
    assert cfg.concurrency == 8
    assert cfg.timeout_sec == 120
    assert cfg.cache_dir == "/tmp/x"
