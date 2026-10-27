# Validation record

Date: 2026-10-27. Initial local environment: Windows, Python 3.12.14.

| Check | Result |
|---|---|
| Unit and CLI suite | 19 tests passed |
| Local wheel build and isolated target installation | Passed; version 0.1.0 |
| Demo JSON and HTML generation | Passed; expected diagnostic exit 2 |
| HTML injection escaping | Passed automated test |
| Linux and Windows CI matrix | Pending first GitHub run |
| Physical server, RAID, SMART, BMC validation | Not performed; those collectors are not implemented |
| Manual HTML visual inspection | Not performed |

The first restricted local test/build attempts could not access their temporary directories. Re-running with the required temporary-file access passed; these were environment permission failures, not passing test results.

Tests use synthetic fixtures for resource, interface, and service behavior. Local Windows demo success does not establish live Linux or physical hardware compatibility. CI results will be recorded separately after execution.
