import type { IngestMetrics, FeatureMetrics } from '../types/ingest';
import { Panel } from './Panel';

export function TrafficMetrics({ metrics, featureMetrics }: { metrics: IngestMetrics; featureMetrics: FeatureMetrics }) {
  return <Panel title="Live traffic" eyebrow="OBSERVATION TELEMETRY"><div className="live-metrics"><div><span>FLOW RATE</span><strong>{metrics.flows_per_second.toFixed(1)} <small>flows/s</small></strong></div><div><span>THROUGHPUT</span><strong>{metrics.throughput_mbps.toFixed(2)} <small>Mbps</small></strong></div><div><span>ACTIVE FLOWS</span><strong>{metrics.active_flows}</strong></div><div><span>FEATURE RATE</span><strong>{featureMetrics.feature_vectors_per_sec.toFixed(1)} <small>vectors/s</small></strong></div><div><span>QUEUE</span><strong>{metrics.queue_size} <small>/ {metrics.queue_maxsize}</small></strong></div><div><span>DROPPED</span><strong className={metrics.events_dropped ? 'warning-text' : ''}>{metrics.events_dropped}</strong></div></div></Panel>;
}
