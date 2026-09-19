import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  ShieldAlert, 
  X, 
  Check, 
  Copy, 
  ExternalLink, 
  AlertCircle, 
  Activity, 
  Clock, 
  Database,
  ArrowRight
} from 'lucide-react';
import type { Alert, Severity } from '../types/contracts';

interface IncidentsViewProps {
  alerts: Alert[];
  selectedAlert: Alert | null;
  onSelectAlert: (alert: Alert | null) => void;
  onAcknowledge: (alertId: string) => Promise<void>;
  onResolve: (alertId: string) => Promise<void>;
}

export const IncidentsView: React.FC<IncidentsViewProps> = ({
  alerts,
  selectedAlert,
  onSelectAlert,
  onAcknowledge,
  onResolve,
}) => {
  const [query, setQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<Severity | 'ALL'>('ALL');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED'>('ALL');
  const [threatClassFilter, setThreatClassFilter] = useState<string>('ALL');
  const [copied, setCopied] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Filter alerts
  const filteredAlerts = alerts.filter((alert) => {
    const matchesQuery = 
      query === '' ||
      `${alert.alert_id} ${alert.flow_id} ${alert.source_ip} ${alert.destination_ip} ${alert.threat_class} ${alert.why_flagged}`
        .toLowerCase()
        .includes(query.toLowerCase());

    const matchesSeverity = severityFilter === 'ALL' || alert.severity === severityFilter;
    const matchesStatus = statusFilter === 'ALL' || alert.status === statusFilter;
    const matchesClass = threatClassFilter === 'ALL' || alert.threat_class === threatClassFilter;

    return matchesQuery && matchesSeverity && matchesStatus && matchesClass;
  });

  const criticalCount = alerts.filter((a) => a.severity === 'CRITICAL' && a.status !== 'RESOLVED').length;
  const newCount = alerts.filter((a) => a.status === 'NEW').length;
  const acknowledgedCount = alerts.filter((a) => a.status === 'ACKNOWLEDGED').length;
  const resolvedCount = alerts.filter((a) => a.status === 'RESOLVED').length;

  const handleCopyEvidence = () => {
    if (!selectedAlert) return;
    void navigator.clipboard.writeText(JSON.stringify(selectedAlert.evidence, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(filteredAlerts, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paladin_incidents_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    const headers = 'alert_id,timestamp,threat_class,severity,confidence,source_ip,destination_ip,status\n';
    const rows = filteredAlerts.map(
      (a) => `${a.alert_id},${a.timestamp},${a.threat_class},${a.severity},${a.confidence_score},${a.source_ip},${a.destination_ip},${a.status}`
    ).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paladin_incidents_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAcknowledge = async (id: string) => {
    setActionLoading(true);
    try {
      await onAcknowledge(id);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async (id: string) => {
    setActionLoading(true);
    try {
      await onResolve(id);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="main-view">
      {/* Header & KPI Summary */}
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <ShieldAlert size={12} /> FORENSIC TRIAGE CONSOLE
          </span>
          <h2>Security Incidents & Alerts</h2>
          <p>
            Correlated cyber threat signals emitted by Paladin's one-way detection enclave.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button className="action-btn" onClick={handleExportCSV} title="Export filtered incidents as CSV">
            <Download size={14} />
            <span>CSV</span>
          </button>
          <button className="action-btn" onClick={handleExportJSON} title="Export filtered incidents as JSON">
            <Download size={14} />
            <span>JSON</span>
          </button>
        </div>
      </div>

      {/* Triage Stats Strip */}
      <div className="kpi-grid">
        <div className="kpi-card crimson">
          <span className="kpi-label">CRITICAL ATTENTION</span>
          <div className="kpi-value" style={{ color: criticalCount > 0 ? '#ff4d6d' : '#fff' }}>
            {criticalCount}
          </div>
          <span className="kpi-sub">Unresolved high-severity events</span>
        </div>

        <div className="kpi-card copper">
          <span className="kpi-label">NEW ALERTS</span>
          <div className="kpi-value">{newCount}</div>
          <span className="kpi-sub">Awaiting operator triage</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">IN INVESTIGATION</span>
          <div className="kpi-value">{acknowledgedCount}</div>
          <span className="kpi-sub">Currently acknowledged</span>
        </div>

        <div className="kpi-card emerald">
          <span className="kpi-label">RESOLVED</span>
          <div className="kpi-value">{resolvedCount}</div>
          <span className="kpi-sub">Audited & closed</span>
        </div>
      </div>

      {/* Toolbar & Filters */}
      <div className="card-panel">
        <div className="table-toolbar">
          <div className="search-wrapper">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search source IP, destination, threat class, flow ID, reason..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {/* Severity Filter Chips */}
          <div className="filter-pills">
            {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((sev) => (
              <button
                key={sev}
                className={`filter-pill ${severityFilter === sev ? 'active' : ''}`}
                onClick={() => setSeverityFilter(sev)}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Status Filter Chips */}
          <div className="filter-pills">
            {(['ALL', 'NEW', 'ACKNOWLEDGED', 'RESOLVED'] as const).map((st) => (
              <button
                key={st}
                className={`filter-pill ${statusFilter === st ? 'active' : ''}`}
                onClick={() => setStatusFilter(st)}
              >
                {st}
              </button>
            ))}
          </div>

          {/* Threat Class Dropdown */}
          <select
            className="action-btn"
            aria-label="Filter by Threat Category"
            value={threatClassFilter}
            onChange={(e) => setThreatClassFilter(e.target.value)}
          >
            <option value="ALL">All Categories</option>
            <option value="DDOS">DDoS</option>
            <option value="C2_BEACON">C2 Beacon</option>
            <option value="DGA_DNS_TUNNEL">DNS Tunnel / DGA</option>
            <option value="RECON">Recon / Portscan</option>
            <option value="DATA_EXFILTRATION">Exfiltration</option>
            <option value="ENCRYPTED_MALWARE">Encrypted Traffic</option>
          </select>
        </div>

        {/* Incidents Table */}
        <div className="data-table-container">
          <table className="pro-table">
            <thead>
              <tr>
                <th>Detected At</th>
                <th>Threat Class</th>
                <th>Severity</th>
                <th>Source IP</th>
                <th>Target IP</th>
                <th>Protocol</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.map((alt) => (
                <tr 
                  key={alt.alert_id} 
                  className={selectedAlert?.alert_id === alt.alert_id ? 'selected' : ''}
                  onClick={() => onSelectAlert(alt)}
                >
                  <td style={{ whiteSpace: 'nowrap' }}>
                    {new Date(alt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td style={{ color: '#fff', fontWeight: 700 }}>
                    {alt.threat_class}
                  </td>
                  <td>
                    <span className={`severity-pill ${alt.severity.toLowerCase()}`}>
                      {alt.severity}
                    </span>
                  </td>
                  <td style={{ color: 'var(--copper-primary)', fontWeight: 600 }}>
                    {alt.source_ip}
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>
                    {alt.destination_ip}
                  </td>
                  <td>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{alt.protocol}</span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 45, height: 4, background: '#1c2434', borderRadius: 2, overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${Math.round(alt.confidence_score * 100)}%`, 
                            height: '100%', 
                            background: alt.confidence_score > 0.9 ? 'var(--threat-critical)' : 'var(--copper-primary)' 
                          }} 
                        />
                      </div>
                      <span style={{ fontSize: '0.72rem' }}>{(alt.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${alt.status.toLowerCase()}`}>
                      {alt.status}
                    </span>
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    {alt.status === 'NEW' && (
                      <button 
                        className="action-btn"
                        style={{ padding: '4px 8px', fontSize: '0.7rem' }}
                        onClick={() => void handleAcknowledge(alt.alert_id)}
                      >
                        Ack
                      </button>
                    )}
                    {alt.status === 'ACKNOWLEDGED' && (
                      <button 
                        className="action-btn"
                        style={{ padding: '4px 8px', fontSize: '0.7rem', color: 'var(--enclave-safe)' }}
                        onClick={() => void handleResolve(alt.alert_id)}
                      >
                        Resolve
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {filteredAlerts.length === 0 && (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No security incidents matched the active query filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slide-Over Incident Investigation Drawer */}
      {selectedAlert && (
        <div className="drawer-backdrop" onClick={() => onSelectAlert(null)}>
          <aside className="incident-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div>
                <span className="eyebrow">
                  <ShieldAlert size={12} /> FORENSIC INCIDENT DOSSIER
                </span>
                <h3 style={{ fontSize: '1.25rem', color: '#fff', margin: '4px 0' }}>
                  {selectedAlert.threat_class}
                </h3>
                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.72rem', color: 'var(--copper-primary)' }}>
                  ID: {selectedAlert.alert_id}
                </span>
              </div>
              <button className="close-btn" onClick={() => onSelectAlert(null)} title="Close Drawer">
                <X size={18} />
              </button>
            </div>

            {/* Severity & Confidence Metric Strip */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ padding: 12, background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 8 }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Severity</span>
                <div style={{ marginTop: 4 }}>
                  <span className={`severity-pill ${selectedAlert.severity.toLowerCase()}`}>
                    {selectedAlert.severity}
                  </span>
                </div>
              </div>

              <div style={{ padding: 12, background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', borderRadius: 8 }}>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Confidence Score</span>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '1.1rem', fontWeight: 800, color: 'var(--copper-primary)', marginTop: 2 }}>
                  {(selectedAlert.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Forensic Narrative */}
            <div>
              <span className="eyebrow">FORENSIC OBSERVATION (WHY FLAGGED)</span>
              <p style={{ fontSize: '0.84rem', color: '#e2e8f0', background: 'rgba(224, 142, 69, 0.06)', border: '1px solid var(--border-amber)', borderRadius: 8, padding: 14, marginTop: 6, lineHeight: 1.5 }}>
                {selectedAlert.why_flagged}
              </p>
            </div>

            {/* Flow Telemetry Parameters */}
            <div>
              <span className="eyebrow">UNIDIRECTIONAL FLOW ATTRIBUTES</span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
                <div className="meta-field">
                  <span>Source Address</span>
                  <strong>{selectedAlert.source_ip}</strong>
                </div>
                <div className="meta-field">
                  <span>Target Address</span>
                  <strong>{selectedAlert.destination_ip}</strong>
                </div>
                <div className="meta-field">
                  <span>Transport Protocol</span>
                  <strong>{selectedAlert.protocol}</strong>
                </div>
                <div className="meta-field">
                  <span>Detector Engine</span>
                  <strong>{selectedAlert.detector} (v{selectedAlert.detector_version})</strong>
                </div>
                <div className="meta-field">
                  <span>Observation Window</span>
                  <strong>{selectedAlert.observation_window_ms} ms</strong>
                </div>
                <div className="meta-field">
                  <span>Signal Occurrences</span>
                  <strong>{selectedAlert.occurrence_count} events</strong>
                </div>
              </div>
            </div>

            {/* Evidence Payload Inspector */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                <span className="eyebrow">RAW EVIDENCE PAYLOAD (METADATA ONLY)</span>
                <button 
                  className="action-btn" 
                  style={{ padding: '2px 8px', fontSize: '0.7rem' }}
                  onClick={handleCopyEvidence}
                >
                  {copied ? <Check size={12} style={{ color: 'var(--enclave-safe)' }} /> : <Copy size={12} />}
                  <span>{copied ? 'Copied' : 'Copy JSON'}</span>
                </button>
              </div>
              <pre className="json-box">
                {JSON.stringify(selectedAlert.evidence, null, 2)}
              </pre>
            </div>

            {/* Triage Action Buttons */}
            <div className="drawer-actions">
              {selectedAlert.status === 'NEW' && (
                <button 
                  className="btn-ack" 
                  disabled={actionLoading}
                  onClick={() => void handleAcknowledge(selectedAlert.alert_id)}
                >
                  {actionLoading ? 'PROCESSING...' : 'ACKNOWLEDGE INCIDENT'}
                </button>
              )}
              {selectedAlert.status !== 'RESOLVED' && (
                <button 
                  className="btn-resolve" 
                  disabled={actionLoading}
                  onClick={() => void handleResolve(selectedAlert.alert_id)}
                >
                  {actionLoading ? 'PROCESSING...' : 'MARK AS RESOLVED'}
                </button>
              )}
            </div>
          </aside>
        </div>
      )}
    </div>
  );
};
