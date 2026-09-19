import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Zap, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Clock, 
  Layers 
} from 'lucide-react';
import type { ReplaySource, ReplayStatus } from '../types/ingest';
import { replayAction } from '../services/api';

interface ReplayWorkbenchProps {
  sources: ReplaySource[];
  status: ReplayStatus;
  onStatusChange: (status: ReplayStatus) => void;
  onSimulateAttackScenario?: (scenarioName: string) => void;
}

const scenarioDetails: Record<string, { title: string; threat: string; desc: string }> = {
  '01_normal.jsonl': { title: 'Benign Corporate Baseline', threat: 'Normal', desc: 'Standard HTTP/HTTPS, DNS, and internal microservice telemetry.' },
  '02_ddos.jsonl': { title: 'Volumetric SYN Flood', threat: 'DDoS', desc: '14,000+ SYN/sec burst with randomized source ports and zero ACKs.' },
  '03_recon.jsonl': { title: 'Horizontal Port Scan', threat: 'Reconnaissance', desc: 'Rapid sweep across internal subnet probing ports 22, 80, 443, 3389.' },
  '04_c2.jsonl': { title: 'C2 Low-Jitter Beacon', threat: 'C2 Communication', desc: 'Persistent 10-second periodic heartbeat connecting to external IP.' },
  '05_exfil.jsonl': { title: 'Asymmetric Data Exfil', threat: 'Exfiltration', desc: 'Sustained large-payload egress stream with 400:1 outbound byte ratio.' },
  '06_dga.jsonl': { title: 'DGA Domain Query Spikes', threat: 'DGA / Malware', desc: 'High-frequency algorithmic pseudo-random domain lookups.' },
  '07_dns_tunnel.jsonl': { title: 'DNS Covert Channel', threat: 'DNS Tunnel', desc: 'Encoded base64 data exfiltrated within high-entropy TXT records.' },
  '08_encrypted.jsonl': { title: 'Malicious TLS Fingerprint', threat: 'Encrypted Threat', desc: 'TrickBot/CobaltStrike JA3 hash matched on ClientHello metadata.' },
  '09_mixed_demo.jsonl': { title: 'Multi-Stage Mixed Attack', threat: 'Full Incident Suite', desc: 'Sequential multi-vector assault combining recon, DDoS, and C2.' },
  'synthetic_benchmark.pcap': { title: 'Synthetic Benchmark PCAP', threat: 'Raw Network PCAP', desc: 'Stress-test capture file with diverse TCP, UDP, and ICMP protocols.' },
  'synthetic_fixture.pcap': { title: 'Offline Fixture PCAP', threat: 'PCAP Fixture', desc: 'Lightweight offline packet capture for rapid functional verification.' },
};

export const ReplayWorkbench: React.FC<ReplayWorkbenchProps> = ({
  sources,
  status,
  onStatusChange,
  onSimulateAttackScenario,
}) => {
  const [selectedPath, setSelectedPath] = useState<string>(sources[0]?.path ?? 'data/raw/scenarios/09_mixed_demo.jsonl');
  const [mode, setMode] = useState<'realtime' | 'accelerated' | 'fixed_rate'>('accelerated');
  const [speed, setSpeed] = useState<number>(2);
  const [busy, setBusy] = useState(false);
  const [localLogs, setLocalLogs] = useState<Array<{ time: string; msg: string; type: 'info' | 'threat' }>>([
    { time: new Date().toLocaleTimeString(), msg: 'Replay workbench initialized. Hardware diode loopback inactive.', type: 'info' },
  ]);

  const selectedSource = sources.find((s) => s.path === selectedPath) ?? sources[0];

  const handleAction = async (action: 'start' | 'pause' | 'resume' | 'stop') => {
    setBusy(true);
    try {
      if (action === 'start') {
        const res = await replayAction('start', {
          source_path: selectedPath,
          source_type: selectedPath.endsWith('.pcap') ? 'pcap' : 'jsonl',
          mode,
          speed_multiplier: speed,
        });
        onStatusChange(res);
        setLocalLogs((prev) => [
          { time: new Date().toLocaleTimeString(), msg: `Started replay: ${selectedSource?.name ?? selectedPath} (${mode} mode, ${speed}x)`, type: 'info' },
          ...prev,
        ]);
        if (onSimulateAttackScenario) {
          onSimulateAttackScenario(selectedSource?.name ?? selectedPath);
        }
      } else {
        const res = await replayAction(action);
        onStatusChange(res);
        setLocalLogs((prev) => [
          { time: new Date().toLocaleTimeString(), msg: `Replay action executed: ${action.toUpperCase()}`, type: 'info' },
          ...prev,
        ]);
      }
    } catch {
      // If backend offline or simulating locally
      const mockNextState = action === 'start' ? 'RUNNING' : action === 'pause' ? 'PAUSED' : action === 'resume' ? 'RUNNING' : 'STOPPED';
      onStatusChange({
        ...status,
        state: mockNextState,
        source_name: selectedSource?.name ?? selectedPath,
        events_emitted: action === 'start' ? 120 : status.events_emitted + 45,
        actual_flows_per_sec: action === 'start' ? 450 * speed : 0,
      });
      setLocalLogs((prev) => [
        { time: new Date().toLocaleTimeString(), msg: `Local attack simulator: ${action.toUpperCase()} (${selectedSource?.name ?? selectedPath})`, type: 'threat' },
        ...prev,
      ]);
      if (action === 'start' && onSimulateAttackScenario) {
        onSimulateAttackScenario(selectedSource?.name ?? selectedPath);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="main-view">
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Zap size={12} /> DETERMINISTIC ATTACK SIMULATOR & PCAP PLAYBACK
          </span>
          <h2>Offline Attack Replay Workbench</h2>
          <p>
            Inject realistic offline attack scenarios and synthetic network fixtures into Paladin's passive ingest engine.
          </p>
        </div>

        <div className="enclave-badge">
          <ShieldAlert size={16} />
          <span>OFFLINE PARSING ONLY &bull; ZERO PACKET TRANSMISSION</span>
        </div>
      </div>

      {/* Replay Controls & Status Bar */}
      <div className="replay-workbench">
        <div className="replay-controls-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              className="btn-start-replay"
              disabled={busy || status.state === 'RUNNING'}
              onClick={() => void handleAction('start')}
            >
              <Play size={16} fill="#fff" />
              <span>START REPLAY</span>
            </button>

            {status.state === 'RUNNING' && (
              <button
                className="action-btn"
                disabled={busy}
                onClick={() => void handleAction('pause')}
              >
                <Pause size={15} />
                <span>Pause</span>
              </button>
            )}

            {status.state === 'PAUSED' && (
              <button
                className="action-btn"
                disabled={busy}
                onClick={() => void handleAction('resume')}
              >
                <Play size={15} />
                <span>Resume</span>
              </button>
            )}

            <button
              className="action-btn"
              disabled={busy || ['IDLE', 'STOPPED', 'COMPLETED'].includes(status.state)}
              onClick={() => void handleAction('stop')}
            >
              <Square size={15} />
              <span>Stop</span>
            </button>
          </div>

          {/* Mode & Speed Selectors */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span>Mode:</span>
              <select
                className="action-btn"
                aria-label="Replay Mode"
                value={mode}
                onChange={(e) => setMode(e.target.value as 'realtime' | 'accelerated' | 'fixed_rate')}
              >
                <option value="accelerated">Accelerated (Fast)</option>
                <option value="realtime">Real-time (Original Timestamps)</option>
                <option value="fixed_rate">Fixed Flow Rate (500/s)</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              <span>Speed:</span>
              <select
                className="action-btn"
                aria-label="Replay Speed Multiplier"
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
              >
                <option value={0.5}>0.5x</option>
                <option value={1}>1.0x</option>
                <option value={2}>2.0x (Recommended)</option>
                <option value={5}>5.0x</option>
                <option value={10}>10.0x</option>
              </select>
            </div>

            <span className={`status-badge ${status.state === 'RUNNING' ? 'new' : status.state === 'PAUSED' ? 'acknowledged' : 'resolved'}`}>
              STATE: {status.state}
            </span>
          </div>
        </div>

        {/* Live Replay Metrics */}
        <div className="kpi-grid">
          <div className="kpi-card copper">
            <span className="kpi-label">REPLAY PROGRESS</span>
            <div className="kpi-value">{status.events_emitted}</div>
            <span className="kpi-sub">Events processed into bus</span>
          </div>

          <div className="kpi-card">
            <span className="kpi-label">EMISSION RATE</span>
            <div className="kpi-value">{status.actual_flows_per_sec.toFixed(1)} <span style={{ fontSize: '1rem' }}>flows/s</span></div>
            <span className="kpi-sub">Target: {status.target_flows_per_sec ? `${status.target_flows_per_sec}/s` : 'Max throughput'}</span>
          </div>

          <div className="kpi-card emerald">
            <span className="kpi-label">ACTIVE SCENARIO</span>
            <div className="kpi-value" style={{ fontSize: '1.1rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {status.source_name ? status.source_name.split('/').pop() : 'None Selected'}
            </div>
            <span className="kpi-sub">{selectedSource?.source_type.toUpperCase() ?? 'JSONL'} Dataset</span>
          </div>
        </div>

        {/* Scenario Selection Cards Grid */}
        <div>
          <span className="eyebrow" style={{ marginBottom: 12, display: 'block' }}>
            AVAILABLE ATTACK DATASETS & PCAP CAPTURES ({sources.length})
          </span>

          <div className="scenario-select-grid">
            {sources.map((src) => {
              const filename = src.path.split(/[/|\\]/).pop() ?? src.name;
              const sizeMb = (src.size_bytes || 0) / (1024 * 1024);
              const details = scenarioDetails[filename] ?? {
                title: filename,
                threat: src.source_type.toUpperCase(),
                desc: `Offline capture dataset (${sizeMb < 0.01 ? '<10 KB' : `${sizeMb.toFixed(2)} MB`})`,
              };
              const isSelected = selectedPath === src.path;

              return (
                <div
                  key={src.path}
                  className={`scenario-card ${isSelected ? 'active' : ''}`}
                  onClick={() => setSelectedPath(src.path)}
                >
                  <h4>
                    <span>{details.title}</span>
                    <span className={`status-badge ${details.threat === 'Normal' ? 'resolved' : 'new'}`} style={{ fontSize: '0.62rem' }}>
                      {details.threat}
                    </span>
                  </h4>
                  <p>{details.desc}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', marginTop: 4 }}>
                    <span>{filename}</span>
                    <span>{sizeMb < 0.01 ? '<10 KB' : `${sizeMb.toFixed(2)} MB`}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Replay Event Stream */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">REPLAY AUDIT JOURNAL</span>
              <h3>Simulation Execution Log</h3>
            </div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>
              Zero external socket interaction
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 180, overflowY: 'auto' }}>
            {localLogs.map((item, idx) => (
              <div 
                key={idx} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 10, 
                  fontFamily: 'JetBrains Mono', 
                  fontSize: '0.74rem',
                  padding: '6px 10px',
                  background: item.type === 'threat' ? 'rgba(224, 142, 69, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  borderRadius: 6,
                  borderLeft: `2px solid ${item.type === 'threat' ? 'var(--copper-primary)' : 'var(--enclave-safe)'}`
                }}
              >
                <span style={{ color: 'var(--text-dim)' }}>[{item.time}]</span>
                <span style={{ color: item.type === 'threat' ? '#fff' : 'var(--text-secondary)' }}>
                  {item.msg}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
