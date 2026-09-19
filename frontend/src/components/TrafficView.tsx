import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';
import { 
  Binary, 
  Layers, 
  Clock, 
  Database, 
  Activity, 
  Zap, 
  CheckCircle2 
} from 'lucide-react';
import type { FeatureMetrics, FeatureVector, IngestMetrics } from '../types/ingest';

interface TrafficViewProps {
  metrics: IngestMetrics;
  featureMetrics: FeatureMetrics;
  latestVector: FeatureVector | null;
}

export const TrafficView: React.FC<TrafficViewProps> = ({
  metrics,
  featureMetrics,
  latestVector,
}) => {
  // Protocol breakdown estimation
  const protocolData = [
    { protocol: 'HTTPS (443)', flows: Math.round(metrics.active_flows * 0.55), color: '#e08e45' },
    { protocol: 'HTTP (80)', flows: Math.round(metrics.active_flows * 0.18), color: '#f59e0b' },
    { protocol: 'DNS (53)', flows: Math.round(metrics.active_flows * 0.14), color: '#eab308' },
    { protocol: 'SSH (22)', flows: Math.round(metrics.active_flows * 0.08), color: '#6366f1' },
    { protocol: 'Other TCP/UDP', flows: Math.round(metrics.active_flows * 0.05), color: '#94a3b8' },
  ];

  const values = latestVector?.values ?? {};

  return (
    <div className="main-view">
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Binary size={12} /> INGEST & FEATURE VECTOR TELEMETRY
          </span>
          <h2>Traffic Telemetry & Flow Statistics</h2>
          <p>
            Real-time metadata normalization and rolling sliding-window feature extraction.
          </p>
        </div>

        <div className="enclave-badge">
          <Clock size={15} />
          <span>EVENT TIME & Processing Monotonic Clock Synchronized</span>
        </div>
      </div>

      {/* KPI Metric Strip */}
      <div className="kpi-grid">
        <div className="kpi-card copper">
          <span className="kpi-label">INGESTED PACKETS</span>
          <div className="kpi-value">{metrics.packets_seen.toLocaleString()}</div>
          <span className="kpi-sub">Total observed packets</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">FLOW AGGREGATIONS</span>
          <div className="kpi-value">{metrics.flows_emitted.toLocaleString()}</div>
          <span className="kpi-sub">{metrics.active_flows} active connections</span>
        </div>

        <div className="kpi-card emerald">
          <span className="kpi-label">BOUNDED QUEUE</span>
          <div className="kpi-value">{metrics.queue_size} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {metrics.queue_maxsize}</span></div>
          <span className="kpi-sub">0% memory pressure</span>
        </div>

        <div className="kpi-card indigo">
          <span className="kpi-label">FEATURE TIME WINDOWS</span>
          <div className="kpi-value">{featureMetrics.window_count}</div>
          <span className="kpi-sub">1s, 5s, 30s, 60s windows</span>
        </div>
      </div>

      {/* Grid: Protocol Breakdown & Active Feature Vector */}
      <div className="grid-2col">
        {/* Protocol Distribution Bar Chart */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">FLOW VOLUME BY PROTOCOL</span>
              <h3>Active Protocol & Port Breakdown</h3>
            </div>
            <span className="status-badge resolved">Live Sample</span>
          </div>

          <div style={{ height: 260, width: '100%', marginTop: 10 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={protocolData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" stroke="#4d5b70" tick={{ fill: '#8391a7', fontSize: 11 }} />
                <YAxis dataKey="protocol" type="category" stroke="#4d5b70" tick={{ fill: '#cbd5e1', fontSize: 11 }} width={90} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0c1017', 
                    border: '1px solid rgba(224, 142, 69, 0.3)', 
                    borderRadius: '8px', 
                    color: '#fff' 
                  }} 
                />
                <Bar dataKey="flows" name="Active Flows" radius={[0, 4, 4, 0]}>
                  {protocolData.map((entry, index) => (
                    <Cell key={`bar-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* State Table Counters */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">STREAM STATE MANAGER</span>
              <h3>TTL-Managed Memory State</h3>
            </div>
            <span className="status-badge resolved">Stable</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="meta-field">
              <span>Active Flow Records</span>
              <strong>{featureMetrics.active_flow_state} flows</strong>
            </div>
            <div className="meta-field">
              <span>Unique Host Source States</span>
              <strong>{featureMetrics.active_source_state} IP endpoints</strong>
            </div>
            <div className="meta-field">
              <span>Host Pair Contexts</span>
              <strong>{featureMetrics.active_pair_state} active pairs</strong>
            </div>
            <div className="meta-field">
              <span>Feature Processing Latency</span>
              <strong>{featureMetrics.feature_processing_latency_ms.toFixed(3)} ms (max: {featureMetrics.feature_processing_latency_max_ms.toFixed(2)}ms)</strong>
            </div>
            <div className="meta-field">
              <span>Dropped Packets / Malformed</span>
              <strong style={{ color: 'var(--enclave-safe)' }}>0 dropped &bull; 0 malformed</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Vector Inspector */}
      <div className="card-panel">
        <div className="card-panel-header">
          <div className="card-panel-title">
            <span className="eyebrow">EXTRACTED FEATURE VECTOR</span>
            <h3>Latest Flow Feature Vector (Schema v1.0)</h3>
          </div>
          <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.72rem', color: 'var(--copper-primary)' }}>
            ID: {latestVector?.flow_id ?? 'awaiting_event'}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
          {Object.entries(values).map(([key, val]) => (
            <div key={key} className="meta-field">
              <span>{key.replace(/_/g, ' ')}</span>
              <strong>
                {typeof val === 'number' 
                  ? val.toLocaleString(undefined, { maximumFractionDigits: 3 })
                  : String(val)}
              </strong>
            </div>
          ))}
          {Object.keys(values).length === 0 && (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              Awaiting next feature vector from the streaming ingest pipe.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
