Exceptions Playbook
-------------------

Principles:
- Time-box and scope exceptions
- Require justification and owner
- Store out-of-tree where possible

Template:

```
id: EX-2024-0001
ruleIds:
  - <OSV/CVE id>
scope:
  repo: my/repo
  path: services/api/
  until: 2024-12-31
owner: team-security
justification: Pending upstream fix; reachable path gated by authz
```


