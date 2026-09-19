# Alert Schema

`Alert` fields include alert ID, event timestamp, flow ID, threat class, subtype, severity, prototype confidence score, source/destination/protocol, normalized evidence, detector and version, optional model version, observation window, scope, replay session, feature schema version, creation/first/last seen times, occurrence count, lifecycle status, evidence completeness, correlation ID, and deterministic explanation.

Statuses are `NEW`, `ACKNOWLEDGED`, and `RESOLVED`. No blocking or mitigation status exists. Detector results remain separate from alerts.
