# Test plan

## Automated layers

1. Unit: inclusive thresholds; NaN/infinity/negative handling; status precedence; memory formula and malformed evidence; load normalization; filesystem capacity; interface state; service state and missing/timeout evidence.
2. Boundary/security: invalid configuration types and unknown keys; duplicate targets; interface traversal; service command injection; HTML escaping; existing output preservation.
3. CLI integration: run a new Python process, parse demo JSON, verify mode/schema/exit code; confirm unsupported live platforms fail clearly; prevent live collectors in demo mode.
4. Packaging: install project and invoke installed `dc-healthcheck --version`.
5. CI: Python 3.11, 3.12, 3.13 on Ubuntu and Windows; actual default Linux collectors must produce three non-UNKNOWN results. Runner-specific load may legitimately trigger alerts.

Run: `python -m unittest discover -s tests -v`. CI workflow: `.github/workflows/ci.yml`.

## Manual lab acceptance (not implied by unit tests)

| Scenario | Method | Expected result |
|---|---|---|
| Normal Linux VM | Run with normal user, default config | Three measurements with valid units |
| Storage threshold | Use a small disposable lab filesystem or fixture; never fill production storage | Warning/critical at configured boundary |
| Inactive service | Configure an already-inactive lab service | CRITICAL with no restart |
| Missing unit/systemd | Select nonexistent unit or use a non-systemd container | UNKNOWN |
| Link down | Inspect a disconnected lab-only interface | WARNING |
| Permission restriction | Restrict fixture access or use a suitable lab account | UNKNOWN; remaining checks continue |
| Output failure | Select nonexistent parent or unwritable target | Clear error and exit 3 |
| Report rendering | Open synthetic HTML on desktop and narrow viewport | Readable table, mode, findings and next steps |
| Performance | Measure ten default runs on local VM storage | Record median/max; investigate target >5 seconds |

No stress tests, cable disconnections, service stops, or destructive storage exercises on production systems are part of this plan. Use synthetic evidence and isolated labs.

## Evidence and acceptance

Record commands, environment, date, pass/fail, and limitations in VALIDATION.md. A configured CI workflow is not evidence of a successful CI run; inspect actual runs. Failed checks must be fixed or explicitly documented before a release claim. Hardware, BMC, and RAID validation remains out of scope until those collectors exist.
