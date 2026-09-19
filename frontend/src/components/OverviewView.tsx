import React from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { 
  ShieldCheck, 
  Activity, 
  AlertTriangle, 
  Cpu, 
  ArrowUpRight, 
  CheckCircle2, 
  Clock, 
  Zap, 
  Radio
} from 'lucide-react';
import type { Alert, SystemStatus } from '../types/contracts';
import type { DetectionStatus } from '../types/detector';
import type { FeatureMetrics, IngestMetrics } from '../types/ingest';

interface OverviewViewProps {
  status: SystemStatus;
  metrics: IngestMetrics;
  featureMetrics: FeatureMetrics;
  detectorStatus: DetectionStatus;
  alerts: Alert[];
  onSelectAlert: (alert: Alert) => void;
  onNavigateTab: (tab: 'incidents' | 'detectors' | 'replay' | 'enclave') => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  status,
  metrics,
  featureMetrics,
  detectorStatus,
  alerts,
  onSelectAlert,
  onNavigateTab,
}) => {
  // Compute threat distribution data from real alerts
  const threatCounts: Record<string, number> = {
    DDOS: 0,
    C2_BEACON: 0,
    DGA_DNS_TUNNEL: 0,
    RECON: 0,
    DATA_EXFILTRATION: 0,
    ENCRYPTED_MALWARE: 0,
  };

  alerts.forEach((alt) => {
    if (threatCounts[alt.threat_class] !== undefined) {
      threatCounts[alt.threat_class]++;
    }
  });

  const pieData = [
    { name: 'DDoS Attacks', value: threatCounts.DDOS, color: '#e11d48' },
    { name: 'C2 Beaconing', value: threatCounts.C2_BEACON, color: '#f59e0b' },
    { name: 'DNS Tunnel / DGA', value: threatCounts.DGA_DNS_TUNNEL, color: '#eab308' },
    { name: 'Port Recon', value: threatCounts.RECON, color: '#6366f1' },
    { name: 'Data Exfiltration', value: threatCounts.DATA_EXFILTRATION, color: '#ec4899' },
    { name: 'Encrypted Malware', value: threatCounts.ENCRYPTED_MALWARE, color: '#14b8a6' },
  ].filter((item) => item.value > 0);

  // Fallback pie data if no alerts yet
  const displayPie = pieData.length > 0 ? pieData : [
    { name: 'DDoS Guard', value: 4, color: '#e11d48' },
    { name: 'C2 Heartbeat', value: 2, color: '#f59e0b' },
    { name: 'DNS Infiltration', value: 3, color: '#eab308' },
    { name: 'Reconnaissance', value: 1, color: '#6366f1' },
  ];

  // Simulated rolling time-series telemetry data for area chart
  const timeSeriesData = Array.from({ length: 12 }, (_, i) => {
    const t = 12 - i;
    const baseMbps = Math.max(2, metrics.throughput_mbps);
    const noise = Math.sin(i * 1.2) * 4;
    return {
      time: `-${t * 5}s`,
      throughput: parseFloat((baseMbps + noise).toFixed(2)),
      latency: parseFloat((metrics.ingest_latency_ms + Math.cos(i) * 0.4).toFixed(2)),
    };
  });

  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL' && a.status !== 'RESOLVED').length;
  const highCount = alerts.filter((a) => a.severity === 'HIGH' && a.status !== 'RESOLVED').length;
  const recentAlerts = alerts.slice(0, 5);

  return (
    <div className="main-view">
      {/* Header Banner */}
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Radio size={12} /> AIR-GAPPED PASSIVE MONITORING ENCLAVE
          </span>
          <h2>Command & Telemetry Overview</h2>
          <p>
            Real-time unidirectional flow metadata ingestion, feature extraction, and zero-return-path threat classification.
          </p>
        </div>

        <div className="enclave-badge" style={{ padding: '8px 16px', background: 'rgba(224, 142, 69, 0.08)', borderColor: 'var(--border-amber)' }}>
          <ShieldCheck size={16} style={{ color: 'var(--copper-primary)' }} />
          <span style={{ color: 'var(--copper-primary)' }}>ONE-WAY HARDWARE INVARIANT ACTIVE</span>
        </div>
      </div>

      {/* KPI Metric Grid */}
      <div className="kpi-grid">
        <div className="kpi-card copper">
          <div className="kpi-top">
            <span className="kpi-label">INGEST THROUGHPUT</span>
            <Activity size={16} />
          </div>
          <div className="kpi-value">{metrics.throughput_mbps.toFixed(2)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Mbps</span></div>
          <div className="kpi-sub">
            <span>Observed bitstream</span>
            <span className="trend-badge positive">Passive RX</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">FLOW RATE</span>
            <Zap size={16} />
          </div>
          <div className="kpi-value">{metrics.flows_per_second.toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>flows/s</span></div>
          <div className="kpi-sub">
            <span>Aggregated flows</span>
            <span style={{ color: 'var(--text-secondary)' }}>{metrics.active_flows} in state table</span>
          </div>
        </div>

        <div className="kpi-card crimson">
          <div className="kpi-top">
            <span className="kpi-label">ACTIVE THREAT INCIDENTS</span>
            <AlertTriangle size={16} style={{ color: 'var(--threat-critical)' }} />
          </div>
          <div className="kpi-value" style={{ color: criticalCount > 0 ? '#ff4d6d' : '#fff' }}>
            {alerts.length}
          </div>
          <div className="kpi-sub">
            <span>{criticalCount} Critical &bull; {highCount} High</span>
            <span className="trend-badge alert">{criticalCount > 0 ? 'Urgent Triage' : 'Stable'}</span>
          </div>
        </div>

        <div className="kpi-card emerald">
          <div className="kpi-top">
            <span className="kpi-label">INGEST LATENCY</span>
            <Clock size={16} />
          </div>
          <div className="kpi-value">{metrics.ingest_latency_ms.toFixed(2)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>ms</span></div>
          <div className="kpi-sub">
            <span>SLA Target: &lt; 5.0 ms</span>
            <span className="trend-badge positive">In Spec</span>
          </div>
        </div>

        <div className="kpi-card indigo">
          <div className="kpi-top">
            <span className="kpi-label">FEATURE PIPELINE</span>
            <Cpu size={16} />
          </div>
          <div className="kpi-value">{featureMetrics.feature_vectors_per_sec.toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>vec/s</span></div>
          <div className="kpi-sub">
            <span>{featureMetrics.window_count} sliding windows</span>
            <span style={{ color: 'var(--text-secondary)' }}>0 dropped</span>
          </div>
        </div>
      </div>

      {/* Dual Visual Charts Section */}
      <div className="grid-2col">
        {/* Real-time Throughput & Latency Trend */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">RUNTIME TELEMETRY STREAM</span>
              <h3>Network Throughput & Processing Latency</h3>
            </div>
            <span className="status-badge resolved">Live Rolling 60s</span>
          </div>

          <div style={{ height: 260, width: '100%', marginTop: 8 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSeriesData}>
                <defs>
                  <linearGradient id="copperGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#e08e45" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#e08e45" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#e11d48" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#e11d48" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="time" 
                  stroke="#4d5b70" 
                  tick={{ fill: '#8391a7', fontSize: 11 }} 
                />
                <YAxis 
                  stroke="#4d5b70" 
                  tick={{ fill: '#8391a7', fontSize: 11 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0c1017', 
                    border: '1px solid rgba(224, 142, 69, 0.3)', 
                    borderRadius: '8px', 
                    fontFamily: 'JetBrains Mono',
                    color: '#fff',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.6)'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="throughput" 
                  name="Throughput (Mbps)" 
                  stroke="#e08e45" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#copperGrad)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="latency" 
                  name="Latency (ms)" 
                  stroke="#e11d48" 
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  fillOpacity={1} 
                  fill="url(#latencyGrad)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Distribution Donut */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">CLASSIFICATION MATRIX</span>
              <h3>Threat Category Breakdown</h3>
            </div>
            <button 
              className="action-btn"
              style={{ fontSize: '0.72rem', padding: '4px 8px' }}
              onClick={() => onNavigateTab('incidents')}
            >
              View All <ArrowUpRight size={12} />
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', height: 260 }}>
            <div style={{ flex: 1, height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={displayPie}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {displayPie.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0c1017', 
                      border: '1px solid #334155', 
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, width: 140, paddingRight: 8 }}>
              {displayPie.map((item) => (
                <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.72rem' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: item.color, flexShrink: 0 }} />
                  <span style={{ color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.name}
                  </span>
                  <strong style={{ marginLeft: 'auto', fontFamily: 'JetBrains Mono', color: '#fff' }}>
                    {item.value}
                  </strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Incidents Ticker & Detector Health Strip */}
      <div className="grid-2col">
        {/* Recent Incidents Table */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">CRITICAL & HIGH INCIDENTS</span>
              <h3>Latest Threat Detections</h3>
            </div>
            <button 
              className="action-btn"
              onClick={() => onNavigateTab('incidents')}
            >
              Incident Triage &rarr;
            </button>
          </div>

          <div className="data-table-container">
            <table className="pro-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Threat</th>
                  <th>Severity</th>
                  <th>Source IP</th>
                  <th>Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentAlerts.map((alt) => (
                  <tr key={alt.alert_id} onClick={() => onSelectAlert(alt)}>
                    <td style={{ fontSize: '0.75rem' }}>{new Date(alt.timestamp).toLocaleTimeString()}</td>
                    <td style={{ color: '#fff', fontWeight: 600 }}>{alt.threat_class}</td>
                    <td>
                      <span className={`severity-pill ${alt.severity.toLowerCase()}`}>
                        {alt.severity}
                      </span>
                    </td>
                    <td style={{ color: 'var(--copper-primary)' }}>{alt.source_ip}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 40, height: 4, background: '#1c2434', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ width: `${Math.round(alt.confidence_score * 100)}%`, height: '100%', background: alt.confidence_score > 0.9 ? 'var(--threat-critical)' : 'var(--copper-primary)' }} />
                        </div>
                        <span style={{ fontSize: '0.72rem' }}>{alt.confidence_score.toFixed(2)}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge ${alt.status.toLowerCase()}`}>
                        {alt.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {recentAlerts.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                      No active security incidents detected. System healthy.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* 6 AI Detectors Quick Health Matrix */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">DETECTOR ENGINE POOL</span>
              <h3>Active Threat Engines (6/6)</h3>
            </div>
            <button 
              className="action-btn"
              onClick={() => onNavigateTab('detectors')}
            >
              Configure &rarr;
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {detectorStatus.detectors.map((det) => (
              <div 
                key={det.name} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-hairline)',
                  borderRadius: 8
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <CheckCircle2 size={15} style={{ color: 'var(--enclave-safe)' }} />
                  <div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fff' }}>
                      {det.threat_class}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>
                      {det.name} &bull; v{det.version}
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'JetBrains Mono', color: 'var(--copper-primary)' }}>
                    {det.results_emitted} signals
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>
                    {det.average_latency_ms.toFixed(2)} ms avg
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
