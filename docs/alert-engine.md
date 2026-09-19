# Alert Engine

Part 7 converts applicable `DetectorResult` objects into a unified assessment, then a canonical SQLite-backed `Alert`. The fusion score selects the strongest weighted detector; agreement, evidence completeness, and optional model scores contribute to prototype confidence. Confidence is not calibrated probability; Part 9 owns calibration.

Severity is an operational prototype policy: LOW below 0.5, MEDIUM at 0.5, HIGH at 0.75, and CRITICAL at 0.9, with limited DDoS impact context. Evidence is normalized into primary, secondary, and derived fields. Deterministic reasons are retained as `why_flagged`.

Deduplication uses source, destination, threat class, subtype, and protocol within 30 seconds. Repeats update occurrence count and last seen. Correlation uses same source and close timestamps; a correlation ID means related observations, not a confirmed attack chain. SQLite migration preserves the Part 1 table.
