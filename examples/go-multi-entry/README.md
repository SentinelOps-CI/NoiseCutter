Go Multi-Entry Sample

This sample demonstrates two entry points with mixed reachability:
 - cmd/server: HTTP server exposing /health, /noop, /do-risky
 - cmd/worker: background job that triggers a vulnerable path

Quickstart:

```bash
make all_artifacts   # sbom -> audit -> reach(server,worker) -> fuse
```

Then enforce policy (server):

```bash
python -m noisecutter policy --sarif report.server.sarif --level high --fail-on reachable
```

Curl demo:

```bash
# Run server
GO111MODULE=on go run ./cmd/server &

# Reachable path
curl -s localhost:8080/do-risky

# Unused path example: none invoked
```


