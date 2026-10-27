# Validation record

Date: 2026-10-27. Initial local environment: Windows, Python 3.12.14.

| Check | Result |
|---|---|
| Unit and CLI suite | 19 tests passed |
| Local wheel build and isolated target installation | Passed; version 0.1.0 |
| Demo JSON and HTML generation | Passed; expected diagnostic exit 2 |
| HTML injection escaping | Passed automated test |
| Linux and Windows CI matrix | All 6 jobs passed: Ubuntu and Windows, Python 3.11, 3.12, 3.13 |
| Live default Linux collectors | Passed in all 3 Ubuntu jobs: load, memory, filesystem |
| Physical server, RAID, SMART, BMC validation | Not performed; those collectors are not implemented |
| Manual HTML visual inspection | Not performed |

The first restricted local test/build attempts could not access their temporary directories. Re-running with the required temporary-file access passed; these were environment permission failures, not passing test results.

Verified code commit: `852dbe3df5415b5f03b41addd0dfed80a8309932`.

CI evidence: [Tests run 40517678394](https://github.com/devmeto5/dc-healthcheck-pro/actions/runs/40517678394). Each matrix job passed package installation, all 19 tests, and the installed command check. All Ubuntu jobs additionally passed the live default-collector smoke test. The subsequent documentation-only validation update does not change the tested code.

Tests use synthetic fixtures for interface and service behavior. Linux CI confirms the default collectors on hosted runners; it does not establish physical hardware compatibility. Real link/service validation and physical-server acceptance remain manual lab tasks.
