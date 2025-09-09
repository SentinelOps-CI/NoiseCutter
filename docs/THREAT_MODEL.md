Threat Model (v0.1)
-------------------

Assets:
- SARIF reports with reachable flags and call paths
- SBOMs and vulnerability inventories

Threats:
- Tampered tool versions or results (syft, OSV API, govulncheck)
- Inaccurate reachability due to reflection/dynamic calls
- Supply-chain drift between source and final artifact

Mitigations:
- Pin tool versions in CI, record versions in SARIF tool.driver
- Accept coverage/eBPF hints to augment static analysis
- Prefer artifact-first SBOMs (image scan) in CI
- Fail closed selectively: only reachable HIGH/CRITICAL block

Assumptions:
- Entry points are defined correctly per project
- OSV availability; fallbacks are documented


