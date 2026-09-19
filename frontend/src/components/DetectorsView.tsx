import React, { useState } from 'react';
import { 
  SlidersHorizontal, 
  CheckCircle2, 
  Zap, 
  Clock, 
  ShieldCheck, 
  Layers, 
  Cpu, 
  Info,
  Terminal,
  Activity
} from 'lucide-react';
import type { DetectionStatus, DetectorResult } from '../types/detector';

interface DetectorsViewProps {
  status: DetectionStatus;
  recentResults: DetectorResult[];
  onTriggerTestSignal: (threatClass: string) => void;
}

interface DetectorMeta {
  title: string;
  threatClass: string;
  mitre: string;
  algorithms: string[];
  description: string;
}

const detectorDescriptions: Record<string, DetectorMeta> = {
  DDOS: {
    title: 'SYN & UDP Flood Engine',
    threatClass: 'DDOS',
    mitre: 'T1498 - Network Denial of Service',
    algorithms: ['SYN/ACK Ratio Variance', 'High-Rate Window Imbalance', 'Source Port Entropy Analysis'],
    description: 'Tracks volumetric burst rates and TCP handshake asymmetry without maintaining connection tables in production.',
  },
  RECON: {
    title: 'Network Recon & Portscan Engine',
    threatClass: 'RECON',
    mitre: 'T1046 - Network Service Discovery',
    algorithms: ['Horizontal IP Sweep Matrix', 'Vertical Destination Port Fanout', 'Failed SYN Ratio'],
    description: 'Detects stealthy horizontal sweeps across internal subnets and aggressive vertical sweeps against edge firewalls.',
  },
  C2_BEACON: {
    title: 'Periodic C2 Beaconing Engine',
    threatClass: 'C2_BEACON',
    mitre: 'T1071.001 - Web Protocols C2',
    algorithms: ['Inter-Arrival Time (IAT) Variance', 'Periodic Jitter Auto-Correlation', 'Burst Regularity Index'],
    description: 'Identifies automated command-and-control heartbeat pulses even when communication uses standard HTTPS ports.',
  },
  DGA_DNS_TUNNEL: {
    title: 'DNS Covert Tunnel & DGA Engine',
    threatClass: 'DGA_DNS_TUNNEL',
    mitre: 'T1071.004 - DNS Tunneling',
    algorithms: ['Shannon Subdomain Entropy', 'Query String Length Anomaly', 'DGA Consonant/Vowel Distribution'],
    description: 'Analyzes passive DNS query metadata to detect data exfiltration via TXT/NULL records and algorithmically generated domains.',
  },
  DATA_EXFILTRATION: {
    title: 'Volume Spike Exfiltration Engine',
    threatClass: 'DATA_EXFILTRATION',
    mitre: 'T1041 - Exfiltration Over C2 Channel',
    algorithms: ['Outbound/Inbound Byte Skew', 'Sustained Egress Volume', 'Anomaly Baseline Distance'],
    description: 'Flags extreme directional byte asymmetries where outbound flow volume exceeds historical baselines by orders of magnitude.',
  },
  ENCRYPTED_MALWARE: {
    title: 'Encrypted TLS/QUIC Metadata Engine',
    threatClass: 'ENCRYPTED_MALWARE',
    mitre: 'T1573 - Encrypted Channel',
    algorithms: ['JA3/JA3S Passive Fingerprinting', 'Cipher Suite Permutation', 'Initial Packet Size Timing Sequence'],
    description: 'Classifies malicious encrypted sessions using pure TLS ClientHello metadata and packet shape with zero payload decryption.',
  },
};

export const DetectorsView: React.FC<DetectorsViewProps> = ({
  status,
  recentResults,
  onTriggerTestSignal,
}) => {
  const [sensitivities, setSensitivities] = useState<Record<string, number>>({
    DDOS: 2,
    RECON: 2,
    C2_BEACON: 2,
    DGA_DNS_TUNNEL: 2,
    DATA_EXFILTRATION: 2,
    ENCRYPTED_MALWARE: 2,
  });

  const handleSensitivityChange = (threatClass: string, val: number) => {
    setSensitivities((prev) => ({ ...prev, [threatClass]: val }));
  };

  return (
    <div className="main-view">
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Cpu size={12} /> PASSIVE INTELLIGENCE HEURISTICS & MODELS
          </span>
          <h2>Threat Detection Engines (6 Active)</h2>
          <p>
            Operating concurrently within the Paladin receive-only enclave. Each engine declares strict scopes and consumes normalized FeatureVectors.
          </p>
        </div>

        <div className="enclave-badge">
          <ShieldCheck size={16} />
          <span>ZERO ACTIVE PROBING &bull; ZERO PACKET INJECTION</span>
        </div>
      </div>

      {/* Detector Performance KPI Strip */}
      <div className="kpi-grid">
        <div className="kpi-card copper">
          <span className="kpi-label">TOTAL ENGINE SIGNALS</span>
          <div className="kpi-value">{status.detector_results_emitted}</div>
          <span className="kpi-sub">Intelligence outputs emitted</span>
        </div>

        <div className="kpi-card emerald">
          <span className="kpi-label">MEAN ENGINE LATENCY</span>
          <div className="kpi-value">{status.average_latency_ms.toFixed(2)} <span style={{ fontSize: '1rem' }}>ms</span></div>
          <span className="kpi-sub">Hardware SLA: &lt; 2.0 ms</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">ACTIVE DETECTORS</span>
          <div className="kpi-value">{status.detector_count} / 6</div>
          <span className="kpi-sub">All families online</span>
        </div>

        <div className="kpi-card indigo">
          <span className="kpi-label">DROPPED SIGNALS</span>
          <div className="kpi-value">{status.detector_results_dropped}</div>
          <span className="kpi-sub">0 queue overflows</span>
        </div>
      </div>

      {/* 6 Detectors Grid */}
      <div className="grid-3col">
        {status.detectors.map((det) => {
          const threatKey = det.threat_class ?? det.name.replace('_detector', '').toUpperCase();
          const meta = detectorDescriptions[threatKey] ?? {
            title: det.name.replace(/_/g, ' ').toUpperCase(),
            threatClass: threatKey,
            mitre: 'T1000 - General Anomaly',
            algorithms: ['Baseline Heuristic'],
            description: 'Passive threat detector engine operating in enclave.',
          };
          const sensitivity = sensitivities[threatKey] ?? 2;

          return (
            <div key={det.name} className="card-panel" style={{ gap: 14 }}>
              <div className="card-panel-header">
                <div className="card-panel-title">
                  <span className="eyebrow">{meta.mitre}</span>
                  <h3 style={{ fontSize: '1rem' }}>{meta.title}</h3>
                </div>
                <span className="status-badge resolved">ACTIVE</span>
              </div>

              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                {meta.description}
              </p>

              {/* Algorithms / Heuristics */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: '0.66rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'JetBrains Mono' }}>
                  Analytical Methods:
                </span>
                {meta.algorithms.map((algo) => (
                  <div key={algo} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    <Layers size={11} style={{ color: 'var(--copper-primary)' }} />
                    <span>{algo}</span>
                  </div>
                ))}
              </div>

              {/* Sensitivity Slider */}
              <div style={{ marginTop: 4, padding: '10px 12px', background: 'var(--bg-subtle)', borderRadius: 8, border: '1px solid var(--border-hairline)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>Sensitivity</span>
                  <span style={{ color: 'var(--copper-primary)', fontWeight: 700, fontFamily: 'JetBrains Mono' }}>
                    {sensitivity === 1 ? 'Conservative' : sensitivity === 2 ? 'Balanced' : 'Aggressive'}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="1"
                  value={sensitivity}
                  onChange={(e) => handleSensitivityChange(meta.threatClass, parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--copper-primary)', cursor: 'pointer' }}
                />
              </div>

              {/* Metrics & Test Trigger Button */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 8, borderTop: '1px solid var(--border-hairline)' }}>
                <div style={{ fontSize: '0.72rem', fontFamily: 'JetBrains Mono', color: 'var(--text-dim)' }}>
                  {det.results_emitted} fired &bull; {det.average_latency_ms.toFixed(2)}ms
                </div>

                <button
                  className="action-btn"
                  style={{ fontSize: '0.72rem', padding: '5px 10px', color: 'var(--copper-primary)' }}
                  onClick={() => onTriggerTestSignal(meta.threatClass)}
                  title="Inject test feature signal for this detector"
                >
                  <Zap size={12} />
                  <span>Test Signal</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Raw Signals Ticker */}
      <div className="card-panel">
        <div className="card-panel-header">
          <div className="card-panel-title">
            <span className="eyebrow">RAW STREAM EMISSIONS</span>
            <h3>Recent Intermediate Detection Signals</h3>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>
            Structured intelligence before alert deduplication and fusion
          </span>
        </div>

        <div className="data-table-container">
          <table className="pro-table">
            <thead>
              <tr>
                <th>Detector</th>
                <th>Threat Class</th>
                <th>Confidence</th>
                <th>Severity</th>
                <th>Window MS</th>
                <th>Scope</th>
              </tr>
            </thead>
            <tbody>
              {recentResults.slice(0, 8).map((res, idx) => {
                const sev = res.severity ?? (res.score > 0.85 ? 'CRITICAL' : res.score > 0.6 ? 'HIGH' : 'MEDIUM');
                return (
                  <tr key={`${res.detector}-${idx}`}>
                    <td style={{ fontFamily: 'JetBrains Mono', color: 'var(--copper-primary)' }}>{res.detector}</td>
                    <td style={{ color: '#fff', fontWeight: 600 }}>{res.threat_class}</td>
                    <td>{(res.score * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`severity-pill ${sev.toLowerCase()}`}>
                        {sev}
                      </span>
                    </td>
                    <td>{res.observation_window_ms ?? 5000} ms</td>
                    <td><span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{res.scope}</span></td>
                  </tr>
                );
              })}
              {recentResults.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                    No recent intermediate detection signals emitted.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
