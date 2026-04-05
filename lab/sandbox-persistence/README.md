# Sandbox Persistence Experiment

## Objective

Determine whether a cloud sandbox container persists across sessions or gets destroyed/recreated.

## Methodology

1. **Baseline**: `bash run_test.sh --baseline` — record environment snapshot + write /tmp markers
2. **Wait**: Let time pass (hours or days)
3. **Compare**: `bash run_test.sh` — check markers, compare with baseline

## Platform Switch Safety

Each platform gets its own `baseline-{hash}.env`. When comparing, the script first checks whether the current platform matches the baseline's platform fingerprint. If they differ, it warns "PLATFORM CHANGED" and refuses to compare — preventing false conclusions.

Example scenario:
- Day 1 on Platform A: `--baseline` → creates `baseline-abc123.env`
- Day 2 on Platform B: run without flag → no matching baseline → warns "run --baseline for this platform"
- Day 3 on Platform A: run without flag → finds `baseline-abc123.env` → compares correctly

## Decision Matrix (same platform only)

| Signal | Container Persisted | Container Recreated |
|--------|-------------------|-------------------|
| CONTAINER_ID | Unchanged | Changed |
| /tmp files | Present | Absent |
| Counter | Incremented | Reset to 1 |
| UPTIME | Growing | Small |

## Trigger Keywords

"持久化检测" / "跑 persistence_test" / "检测沙盒"
