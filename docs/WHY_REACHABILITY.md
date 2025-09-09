Why Reachability
----------------

Traditional SCA flags vulnerable packages regardless of whether the vulnerable code is ever invoked. NoiseCutter adds call-path evidence to identify advisories that are actually reachable from defined entry points.

Principles:
- Focus on artifact-accurate SBOMs (source and final images)
- Map advisories to components using OSV
- Determine reachability with static analysis plus coverage hints
- Normalize to SARIF, enforce CI policy only on reachable HIGH/CRITICAL

Limitations (v0.1): no auto-fixes, no bespoke feeds, no full dynamic exploit proofs.


