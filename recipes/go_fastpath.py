from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional


def run_go_coverage(entry: Path, out_path: Path) -> Optional[Path]:
    if not (entry.exists() and entry.is_dir()):
        return None
    cover = out_path
    # Attempt to run tests with coverage; if project has tests,
    # this will generate hints.
    try:
        subprocess.run(
            ["go", "test", "./...", f"-coverprofile={cover}"],
            check=True,
        )
        return cover
    except Exception:
        return None


def go_pr_fastpath(
    repo_root: Path,
    entry: Path,
    sbom_out: Path,
    vulns_out: Path,
    reach_out: Path,
    sarif_out: Path,
) -> None:
    from noisecutter.integrations.syft_adapter import generate_sbom
    from noisecutter.integrations.osv_adapter import audit_osv
    from noisecutter.integrations.go.govulncheck_adapter import (
        compute_reachability_go,
    )
    from noisecutter.core.fuse import fuse_to_sarif

    sbom_doc = generate_sbom(source_path=repo_root, image_ref=None)
    sbom_out.write_text(json.dumps(sbom_doc, indent=2))

    vulns_doc = audit_osv(sbom_path=sbom_out)
    vulns_out.write_text(json.dumps(vulns_doc, indent=2))

    coverage_path = run_go_coverage(
        entry=entry,
        out_path=repo_root / "coverage.out",
    )
    reach_doc = compute_reachability_go(
        entry_path=entry,
        vulns_json=vulns_out,
        coverage_path=coverage_path,
    )
    reach_out.write_text(json.dumps(reach_doc, indent=2))

    sarif_doc = fuse_to_sarif(
        sbom_path=sbom_out,
        vulns_path=vulns_out,
        reach_path=reach_out,
    )
    sarif_out.write_text(json.dumps(sarif_doc, indent=2))
