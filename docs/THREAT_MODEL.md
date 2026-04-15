Threat model (overview)
=========================

This document summarizes assets, threats, and mitigations for NoiseCutter **v0.1.x**. For how mitigations map to GitHub Actions and release automation, see [INTEGRATIONS.md](INTEGRATIONS.md).

Assets
------

- SARIF reports with reachability flags and call-path hints
- SBOMs and vulnerability inventories produced or consumed by the tool
- CI logs and published packages (wheels, container images)

Threats
-------

- **Tampered or mismatched tool versions** (Syft, govulncheck) affecting SBOM or reach results
- **Tampered or spoofed OSV API responses** (network attacker or misconfiguration)
- **Inaccurate reachability** due to reflection, dynamic dispatch, or incomplete static analysis
- **Supply-chain drift** between source tree and deployed artifact (image vs repo scan)

Mitigations
-----------

- **Pin tool versions** in CI and in `tool-versions.json`; prefer checksum-verified Syft installs ([`scripts/install-syft.sh`](../scripts/install-syft.sh))
- **Record** tool identity in SARIF where possible (`tool.driver`)
- **Retry and harden** OSV HTTP usage (timeouts, backoff on transient failures)
- **CI gates:** ruff, mypy, tests, **pip-audit** on locked runtime dependencies, **CodeQL** for Python, optional **dependency review** on PRs
- **Release pipeline:** PyPI via **trusted publishing (OIDC)**, **artifact attestations** for `dist/*` on tag builds (see [INTEGRATIONS.md](INTEGRATIONS.md)), container images pushed to GHCR
- **Policy:** fail selectively on **reachable** HIGH/CRITICAL per [`policy`](../policy/default_policy.yaml) / CLI

Assumptions
-----------

- Entry points reflect real program entry; misconfiguration yields misleading reachability.
- OSV and external tools are available; behavior when offline is limited to cached data where implemented.
