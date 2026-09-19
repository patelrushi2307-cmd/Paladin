import type { FeatureVector } from '../types/ingest';
import { Panel } from './Panel';

function display(vector: FeatureVector | null, name: string): string {
  if (!vector || !vector.availability[name] || vector.values[name] === null || vector.values[name] === undefined) return 'N/A';
  const value = vector.values[name];
  return typeof value === 'number' ? value.toFixed(3) : String(value);
}

export function FeatureInspector({ vector }: { vector: FeatureVector | null }) {
  return <Panel title="Feature inspector" eyebrow="DEVELOPER VIEW" className="inspector"><div className="inspector-meta"><span>SCOPE <b>{vector?.scope ?? 'N/A'}</b></span><span>SOURCE <b>{vector?.source_type ?? 'N/A'}</b></span><span>SCHEMA <b>{vector?.feature_schema_version ?? 'N/A'}</b></span></div><div className="feature-values"><div><h3>TRAFFIC</h3><p>Packets/sec <b>{display(vector, 'packets_per_sec')}</b></p><p>Bytes/sec <b>{display(vector, 'bytes_per_sec')}</b></p><p>Total bytes <b>{display(vector, 'bytes_total')}</b></p></div><div><h3>TEMPORAL</h3><p>IAT mean <b>{display(vector, 'iat_mean')}</b></p><p>IAT CV <b>{display(vector, 'iat_cv')}</b></p><p>Periodicity <b>{display(vector, 'periodicity_score')}</b></p></div><div><h3>DIVERSITY</h3><p>Dest. hosts <b>{display(vector, 'unique_dst_hosts')}</b></p><p>Dest. ports <b>{display(vector, 'unique_dst_ports')}</b></p><p>Source entropy <b>{display(vector, 'source_ip_entropy')}</b></p></div><div><h3>DNS / TLS</h3><p>DNS entropy <b>{display(vector, 'dns_query_entropy')}</b></p><p>TLS metadata <b>{display(vector, 'tls_metadata_available')}</b></p><p>Packet size <b>{display(vector, 'packet_size_mean')}</b></p></div></div>{!vector && <div className="details-empty"><span>+</span><strong>No feature vector observed</strong><small>Start a passive replay to inspect derived telemetry.</small></div>}</Panel>;
}
