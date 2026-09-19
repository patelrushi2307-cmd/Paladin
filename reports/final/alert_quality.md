# Alert Quality

The compact mixed scenario produced 36 FlowEvents, 36 FeatureVectors, 216 DetectorResults, and 32 persisted Alerts. The synthetic PCAP fixture produced 22 flows, 132 DetectorResults, and 13 persisted Alerts. These are behavioral fixture runs, not precision/recall evaluations.

The alert count is higher than the input count because multiple applicable detector families may emit independent intelligence for the same observation, while deduplication merges repeated keys within the configured window. A formal benign-period false-positive rate requires aligned ground truth windows and is not claimed here.

Every persisted alert is required to carry threat class, severity, prototype confidence score, source/destination, detector/version, structured evidence, why_flagged, scope, occurrence count, and lifecycle status.
