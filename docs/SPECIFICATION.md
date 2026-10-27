# Technical specification

Project: DC HealthCheck Pro · Target: v0.1.0 · Owner: devmeto5

## Purpose and users

Provide repeatable, evidence-based local server triage. A Data Center Technician uses link and capacity findings during handover or incident checks. A System Administrator uses resource and service checks before maintenance or during investigation. A portfolio reviewer can run synthetic examples without a server.

This tool reports symptoms and next steps; it does not claim root-cause diagnosis or equipment certification.

## Functional requirements and acceptance

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | Local CLI with help/version, config, demo, format, and output options | CLI and entry-point tests |
| FR-02 | One-minute load normalized by logical CPU count | Fixture 4/4 produces 1.0 and warning |
| FR-03 | Memory usage from MemAvailable | 1000 total/600 available yields 40% |
| FR-04 | Capacity for explicit filesystem paths | 90% at default thresholds is critical |
| FR-05 | Operational state for selected interfaces | Up=OK, down=WARNING, unknown=UNKNOWN |
| FR-06 | Activity for explicit systemd service units | Active=OK, inactive/failed=CRITICAL; unavailable=UNKNOWN |
| FR-07 | Strict TOML config and inclusive thresholds | Reject invalid ranges, nonfinite numbers, unknown keys and duplicate targets |
| FR-08 | Text, JSON, and escaped standalone HTML | JSON parse test, injection test, report file checks |
| FR-09 | Useful exit status and partial-result handling | Critical dominates unknown; unknown dominates warning |
| FR-10 | Demo independent of the running host | Live collector is forbidden in demo test |
| FR-11 | Read-only collection with bounded service commands | Argument-list subprocess tests, no remediation commands |
| FR-12 | Reproducible public repository | English docs, installation instructions, automated workflow, validation record |

## Data contract

JSON schema version `1.0` contains `tool_version`, UTC ISO-8601 `generated_at`, `mode` (LIVE or DEMO), overall `status`, and `checks`. Each check has a stable identifier, status, summary, recommendation, optional numeric value, and optional unit. Unavailable values are JSON null; NaN and infinity are rejected. Consumers must inspect mode and individual results. Breaking changes to this contract require a schema-version change.

## Configuration contract

Top-level TOML keys: `load`, `memory`, `disk` (two numeric thresholds); `paths`, `interfaces`, `services` (unique string arrays); `timeout` (service command seconds). No arbitrary commands or plugins can be loaded from configuration. Input is limited to 64 KiB; each target list has at most 64 entries. Each threshold pair requires 0 <= warning < critical; percentage critical is at most 100. Timeout must be greater than 0 and at most 30 seconds. Service names must explicitly end in `.service`; interface names cannot traverse directories.

## Nonfunctional requirements

- Standard-library runtime, Python 3.11–3.13 test matrix; Linux for real measurements and cross-platform demo.
- No automatic privilege elevation, system mutation, credential collection, or network requests.
- A failed collector does not discard the other findings. Recognized collection errors become UNKNOWN.
- HTML escapes all dynamic content and has no scripts, CDN assets, or tracking.
- Report creation refuses overwrite. Raw command stderr and host identifiers are not automatically included.
- Default three-check run targets under five seconds on an unstalled local filesystem. This is a target, not a hard deadline guarantee.
- Service command worst-case duration is the number of selected services multiplied by timeout, plus local collection overhead.
- English source, documentation, examples, and reports.

## Exclusions and release gates

Hardware health, storage controller status, BMC integrations, multi-host scanning, scheduled monitoring, authentication, databases, web services, and remediation are excluded from v0.1.0. No blanket claim of production readiness is permitted.

Release gates: all automated tests pass; package installation and CLI work; demo reports are valid; Linux CI verifies real default collectors; no secrets or real infrastructure reports are committed; README separates supported functionality from roadmap. Physical-server compatibility must be recorded separately before claiming it.
