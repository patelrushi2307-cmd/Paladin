export interface DetectorStatus {
  name: string;
  enabled: boolean;
  status: string;
  version: string;
  scopes: string[];
  model_available?: boolean;
  results_emitted: number;
  errors: number;
  average_latency_ms: number;
  threat_class?: string;
}

export interface DetectionStatus {
  active_detectors: string[];
  detector_count: number;
  detector_results_emitted: number;
  detector_results_dropped: number;
  average_latency_ms: number;
  errors: number;
  detectors: DetectorStatus[];
}

export interface DetectorResult {
  detector: string;
  detector_version: string;
  threat_class: string;
  detected: boolean;
  score: number;
  evidence: Record<string, unknown>;
  reasons: string[];
  scope: string;
  subtype?: string;
  applicability: string;
  evidence_completeness: number;
  severity?: string;
  observation_window_ms?: number;
}
