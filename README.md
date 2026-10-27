# DC HealthCheck Pro

Read-only Linux server diagnostics for Data Center Technicians and System Administrators.

Maintained by [devmeto5](https://github.com/devmeto5). Version **0.1.0** is an initial functional release, not a hardware certification tool.

## What it does

- Checks one-minute load per logical CPU, available memory, and capacity of selected filesystem paths.
- Checks operational state of explicitly selected network interfaces and activity of selected systemd services.
- Produces terminal, JSON, and self-contained HTML reports with evidence and suggested next steps.
- Returns OK, WARNING, CRITICAL, or UNKNOWN; unavailable evidence is never reported as healthy.
- Runs a synthetic demonstration on Windows, Linux, or macOS without inspecting the host.

No runtime dependencies beyond Python 3.11+. Live checks require Linux. Checks do not restart services, change settings, run stress tests, or contact remote systems. The only requested writes are report files.

## Quick start

```bash
git clone https://github.com/devmeto5/dc-healthcheck-pro.git
cd dc-healthcheck-pro
python -m dc_healthcheck --demo
python -m dc_healthcheck --demo --format html --output demo-report.html
```

The demo deliberately includes a disk alert and exits with **2**. That is an expected diagnostic result, not a crash. Open `demo-report.html` in a browser.

Optional installation in a virtual environment:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
dc-healthcheck --version
```

## Live Linux assessment

```bash
python -m dc_healthcheck --config config.example.toml
python -m dc_healthcheck --config config.example.toml --format json --output server-report.json
```

Use a normal account first. The default profile checks load, memory, and `/`. Set `interfaces = ["eth0"]` and `services = ["sshd.service"]` only after confirming the actual names expected on your server. Optional checks are not auto-discovered. Output files must not already exist; parent directories must exist.

Threshold comparisons are inclusive. Load defaults to warning at 1.0 and critical at 2.0 per logical CPU; this includes waiting tasks and is **not CPU utilization**. Memory uses `(MemTotal - MemAvailable) / MemTotal`. Filesystem usage uses `shutil.disk_usage().used / total`; reserved blocks may make it differ from `df`'s percentage. Defaults are illustrative baselines and should be tuned to a workload.

| Exit | Meaning |
|---|---|
| 0 | All requested checks OK |
| 1 | Warning, no critical or unknown checks |
| 2 | At least one known critical condition |
| 3 | Unknown evidence without a known critical, or a configuration/output error |

Overall priority: CRITICAL > UNKNOWN > WARNING > OK. Individual unknowns remain visible even when a critical determines the exit code. Command-line syntax errors use argparse's exit code 2 and print usage; they produce no report.

## Development and verification

```bash
python -m unittest discover -s tests -v
```

CI installs the package, tests Python 3.11–3.13 on Linux and Windows, and runs a live Linux smoke assessment. See [test plan](docs/TEST_PLAN.md) and [validation record](docs/VALIDATION.md) for the distinction between automated evidence and hardware validation.

## Project documents

- [Technical specification and acceptance criteria](docs/SPECIFICATION.md)
- [Architecture and design decisions](docs/ARCHITECTURE.md)
- [Implementation roadmap](docs/ROADMAP.md)
- [Testing strategy](docs/TEST_PLAN.md)
- [Operational runbook](docs/RUNBOOK.md)
- [Contribution guide](CONTRIBUTING.md)

## Scope and limitations

This release is a local point-in-time assessment. It does not implement SMART/NVMe, RAID, IPMI/Redfish, thermal sensors, ECC checks, network reachability, remote fleet access, continuous monitoring, or automatic remediation. Containers may expose host-wide load and memory; cgroup-aware metrics are deferred. Local filesystem calls can block on stalled storage; only external service commands have a timeout. Reports can contain configured paths, interfaces, and unit names; review them before sharing. No live machine report is bundled with the project.

Source is published for portfolio review. No open-source license is selected yet; public visibility alone does not grant a software license.
