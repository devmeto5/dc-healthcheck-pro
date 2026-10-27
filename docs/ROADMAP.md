# Implementation roadmap

## Phase 1 — Foundation and specification
Define personas, checks, status contract, safe defaults, and release gates. Deliver specification, architecture, repository skeleton, and configuration example.

## Phase 2 — Functional v0.1.0
Implement local Linux load, memory, filesystem, explicit interface, and explicit service checks. Add portable demo, text/JSON/HTML reports, strict config, collector isolation, and documented exit codes. Deliver a working CLI without runtime third-party dependencies.

## Phase 3 — Verification and publication
Run unit and subprocess tests locally, verify installation, generate synthetic examples, upload the project, and inspect CI. Record platform and scope of verification. Publish only synthetic reports. Complete a manual Linux VM run before describing virtualized deployment support as validated.

## Phase 4 — Hardware-focused v0.2 (planned, not implemented)
Add smartctl JSON/NVMe fixtures, thermal readings, RAID adapters where documented, and clear privilege/unsupported-device reporting. Test permission denial, absent utilities, malformed output, vendor differences, and degraded hardware simulations. Never start SMART self-tests implicitly. Require a dedicated lab and user-approved devices for hardware exercises.

## Phase 5 — Operations v0.3 (planned, not implemented)
Add baseline comparison, inode usage, structured finding codes, optional explicit network reachability targets, and cgroup-aware reporting. Consider SSH execution only with a separate credential and host-verification design. Keep network checks opt-in and narrowly targeted.

## Phase 6 — Stable v1.0 (planned)
Confirm supported distributions and hardware profiles, test report schema compatibility, complete threat review, select a license, and document operational limits. Add release packaging and changelog automation only after release acceptance is reproducible.

Each phase ends with working deliverables and evidence. Calendar estimates depend on access to Linux VMs, hardware, and the intended vendor support matrix; no completion dates are assumed.
