# Model Input Contract

`FeatureVector` is the stable input boundary for Parts 4-6. Detectors do not depend on Scapy, PCAP, replay, or frontend modules.

## Schema

Each vector has `feature_id`, `flow_id`, event-time `timestamp`, optional `window_start`/`window_end`, explicit `scope`, `source_type`, grouped values, flat `values`, `availability`, and `feature_schema_version` (`1.0`).

## Ordering and missing values

Use `to_model_vector(feature_vector, feature_list)` with an explicit ordered feature list. It returns values in exactly that order and raises when a required feature is unavailable. No implicit sorting, zero filling, or model inference is performed. `N/A` in the dashboard represents `null` plus unavailable metadata.

## Types and preprocessing

Raw counters and rates remain meaningful units. Booleans and strings such as protocol, TLS version, and ALPN remain categorical metadata. Scaling, encoding, imputation policy, and training-only transformations belong to the model preprocessing layer and must be versioned with the model.

## Reproducibility

Given the same ordered flow sequence, state expiration configuration, and feature schema version, vectors are deterministic. `feature_id` is UUID5-derived from event identity, scope, and event timestamp. No random model or trained artifact exists in Part 3.

## Detector handoff

A detector receives a `FeatureVector` and context through `ThreatDetector.detect(feature_vector, context)`. It must treat unavailable values as unavailable, keep feature derivation separate from classification, and never access raw packets or network adapters.
