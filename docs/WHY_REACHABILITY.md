Why reachability
================

Traditional SCA flags vulnerable packages even when the vulnerable code is never executed on a path that matters for your deployment. NoiseCutter adds **reachability context**: which advisories are plausibly reachable from **defined entry points**, combined with SBOM and OSV data, and normalized to **SARIF** for policy gates in CI.

Principles
----------

- Prefer **accurate SBOMs** (source tree and/or built images as appropriate)
- Map advisories to components with **OSV**
- Combine **static reachability** (for example govulncheck for Go) with optional coverage hints where supported
- Enforce policy in CI on **reachable** high-severity findings rather than on raw dependency noise alone

Limitations (current)
---------------------

- No automatic remediation or patch application
- No proprietary vulnerability feeds beyond what integrations implement
- Reachability is **static analysis–biased**; dynamic exploit proof is out of scope for the core CLI

See also [QUICKSTART.md](QUICKSTART.md), [THREAT_MODEL.md](THREAT_MODEL.md), and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
