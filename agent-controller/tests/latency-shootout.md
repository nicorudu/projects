# Path A (Wi-Fi) vs Path B (USB) shoot-out

Method: [blueprint §9](../docs/agent-controller-v0-blueprint.md#9-build-sequence). 50 runs per test per path; record the median and 95th percentile (p95).

Firmware version: ___ · Companion app version: ___ · Date: ___

| Test | Path A median | Path A p95 | Path B median | Path B p95 | Target |
|---|---|---|---|---|---|
| Key press → event at Mac (ms) | | | | | < 50 |
| Voice key → first audio frame at Mac (ms) | | | | | < 100 |
| Release → cleaned text on dock (s) | | | | | < 1.5 |
| Mac update → pixels on dock (ms) | | | | | < 100 |
| Audio frames dropped per minute | | | | | 0 |
| Controller battery, idle (h) | | | | | |
| Controller battery, mixed use (h) | | | | | ≥ 8 |

**Decision:** default path = ___ because ___
