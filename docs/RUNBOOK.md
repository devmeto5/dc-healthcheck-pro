# Operator runbook

1. Confirm the intended Linux host, workload, and selected filesystem paths. Start with a normal user account.
2. Review config thresholds and opt-in links/services. A link-down warning only matters if that interface should be active.
3. Run the command and retain the report in an approved local directory. Do not use exit code alone; inspect all findings and mode.
4. For CRITICAL, confirm the reading using the relevant operating-system tools and follow your incident process. For UNKNOWN, investigate unavailable evidence before declaring the server healthy.
5. Investigate load with process and I/O tools, memory with available-memory observations, storage with capacity/retention review, links with cable/optics/switch-port checks, and services with their logs and dependencies.
6. Obtain normal operational authorization before any remediation. This tool never performs it.
7. Review paths and service/interface names before sharing a report. Use `--demo` for portfolio screenshots.

Troubleshooting: on Windows use `--demo`; a container without systemd cannot validate service activity; an existing output file requires a new filename; UNKNOWN interface state is not proof of failed connectivity. A successful local link check does not test DNS, routing, packet loss, or remote reachability.
