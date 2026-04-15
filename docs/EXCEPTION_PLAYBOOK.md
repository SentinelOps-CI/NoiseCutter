Exceptions playbook
====================

Principles
----------

- Time-box and scope every exception
- Require justification and a named owner
- Prefer storing exception metadata outside the default policy file when your organization allows it

Template (YAML-style)
---------------------

Use a unique id and an explicit expiry where possible:

```yaml
id: EX-2026-0001
ruleIds:
  - OSV-2026-00000
scope:
  repo: org/service
  path: services/api/
  until: "2026-12-31"
owner: team-security
justification: Pending upstream fix; reachable path gated by authorization controls
```

Review exceptions on a schedule; remove or renew before `until` passes.

Related documentation
-----------------------

- Default policy example: [`policy/default_policy.yaml`](../policy/default_policy.yaml)
- CLI policy command: `noisecutter policy --help`
