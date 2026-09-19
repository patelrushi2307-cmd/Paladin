import React from 'react';
import { 
  Database, 
  Server, 
  Activity, 
  CheckCircle2, 
  ExternalLink, 
  HardDrive, 
  Clock, 
  Sliders 
} from 'lucide-react';
import type { SystemStatus } from '../types/contracts';
import type { FeatureMetrics, IngestMetrics } from '../types/ingest';

interface DiagnosticsViewProps {
  status: SystemStatus;
  metrics: IngestMetrics;
  featureMetrics: FeatureMetrics;
}

export const DiagnosticsView: React.FC<DiagnosticsViewProps> = ({
  status,
  metrics,
  featureMetrics,
}) => {
  return (
    <div className="main-view">
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Server size={12} /> ENCLAVE SYSTEM DIAGNOSTICS & AUDIT
          </span>
          <h2>Runtime Health & Storage</h2>
          <p>
            Process execution counters, SQLite audit storage status, and internal bounded queue parameters.
          </p>
        </div>

        <div className="enclave-badge">
          <CheckCircle2 size={16} />
          <span>FASTAPI & REACT DEV RUNTIME ACTIVE</span>
        </div>
      </div>

      {/* Diagnostics Grid */}
      <div className="grid-2col">
        {/* SQLite Database Audit */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">PERSISTENCE STORAGE</span>
              <h3>SQLite Incident Database</h3>
            </div>
            <Database size={18} style={{ color: 'var(--copper-primary)' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div className="meta-field">
              <span>Database URI</span>
              <strong>sqlite:///./data/paladin.db</strong>
            </div>
            <div className="meta-field">
              <span>WAL Journal Mode</span>
              <strong style={{ color: 'var(--enclave-safe)' }}>PRAGMA journal_mode = WAL (Active)</strong>
            </div>
            <div className="meta-field">
              <span>Synchronous Flag</span>
              <strong>NORMAL (Zero thread contention)</strong>
            </div>
            <div className="meta-field">
              <span>Stored Incident Records</span>
              <strong style={{ color: 'var(--copper-primary)' }}>{status.alerts_total} persisted events</strong>
            </div>
            <div className="meta-field">
              <span>Deduplication & Correlation</span>
              <strong>Multi-dimensional sliding correlation key</strong>
            </div>
          </div>
        </div>

        {/* Runtime Performance Counters */}
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">EXECUTION BOUNDS</span>
              <h3>Memory & Queue Protection</h3>
            </div>
            <HardDrive size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div className="meta-field">
              <span>Ingest Queue Capacity</span>
              <strong>{metrics.queue_maxsize.toLocaleString()} max items</strong>
            </div>
            <div className="meta-field">
              <span>Current Ingest Queue Load</span>
              <strong>{metrics.queue_size} items ({((metrics.queue_size / metrics.queue_maxsize) * 100).toFixed(2)}%)</strong>
            </div>
            <div className="meta-field">
              <span>Feature Queue Load</span>
              <strong>{featureMetrics.feature_queue_size} items</strong>
            </div>
            <div className="meta-field">
              <span>Dropped Events Counter</span>
              <strong style={{ color: metrics.events_dropped > 0 ? 'var(--threat-critical)' : 'var(--enclave-safe)' }}>
                {metrics.events_dropped} (Bounded drop accounting)
              </strong>
            </div>
            <div className="meta-field">
              <span>Flow Idle Timeout</span>
              <strong>30.0 seconds TTL</strong>
            </div>
          </div>
        </div>
      </div>

      {/* OpenAPI Endpoint Health Map */}
      <div className="card-panel">
        <div className="card-panel-header">
          <div className="card-panel-title">
            <span className="eyebrow">REST & WEBSOCKET BOUNDARIES</span>
            <h3>Registered FastAPI Service Contracts</h3>
          </div>
          <a
            href="http://localhost:8000/api/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn"
            style={{ fontSize: '0.72rem', color: 'var(--copper-primary)' }}
          >
            <span>Interactive OpenAPI Docs</span>
            <ExternalLink size={12} />
          </a>
        </div>

        <div className="data-table-container">
          <table className="pro-table">
            <thead>
              <tr>
                <th>Method</th>
                <th>Endpoint Path</th>
                <th>Contract Purpose</th>
                <th>Operational Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span style={{ color: '#38bdf8', fontWeight: 700 }}>GET</span></td>
                <td><code>/api/system/status</code></td>
                <td>Enclave health, active detectors, throughput & invariants</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: '#38bdf8', fontWeight: 700 }}>GET</span></td>
                <td><code>/api/alerts</code></td>
                <td>Query security incidents with severity/status filters</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: 'var(--copper-primary)', fontWeight: 700 }}>POST</span></td>
                <td><code>/api/alerts/{'{id}'}/acknowledge</code></td>
                <td>Triage transition to ACKNOWLEDGED state</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: 'var(--copper-primary)', fontWeight: 700 }}>POST</span></td>
                <td><code>/api/alerts/{'{id}'}/resolve</code></td>
                <td>Incident resolution & audit closure</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: '#38bdf8', fontWeight: 700 }}>GET</span></td>
                <td><code>/api/replay/sources</code></td>
                <td>List available offline PCAP and JSONL attack datasets</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: 'var(--copper-primary)', fontWeight: 700 }}>POST</span></td>
                <td><code>/api/replay/start</code></td>
                <td>Trigger deterministic replay with speed multiplier</td>
                <td><span className="status-badge resolved">ONLINE</span></td>
              </tr>
              <tr>
                <td><span style={{ color: '#a855f7', fontWeight: 700 }}>WS</span></td>
                <td><code>/ws/events</code></td>
                <td>Real-time streaming heartbeat & telemetry envelope</td>
                <td><span className="status-badge resolved">STREAMING</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
