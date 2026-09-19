import React, { useEffect, useRef, useState } from 'react';
import { Navigation, type ActiveTab } from '../components/Navigation';
import { OverviewView } from '../components/OverviewView';
import { IncidentsView } from '../components/IncidentsView';
import { DetectorsView } from '../components/DetectorsView';
import { TrafficView } from '../components/TrafficView';
import { ReplayWorkbench } from '../components/ReplayWorkbench';
import { EnclaveArchitectureView } from '../components/EnclaveArchitectureView';
import { DiagnosticsView } from '../components/DiagnosticsView';
import { playAlertChime } from '../utils/sound';
import {
  mockAlerts,
  mockSystemStatus,
  mockIngestMetrics,
  mockFeatureMetrics,
  mockDetectionStatus,
  defaultReplaySources,
  mockFeatureVector,
} from '../utils/mockData';
import {
  getAlerts,
  getDetectorResults,
  getDetectorStatus,
  getRecentFeatures,
  getReplaySources,
  getSystemStatus,
  acknowledgeAlert,
  resolveAlert,
} from '../services/api';
import type { Alert, SystemStatus } from '../types/contracts';
import type { DetectionStatus, DetectorResult } from '../types/detector';
import type { FeatureMetrics, FeatureVector, IngestMetrics, ReplaySource, ReplayStatus } from '../types/ingest';

const initialReplay: ReplayStatus = {
  state: 'IDLE',
  replay_session_id: null,
  source_name: null,
  source_type: null,
  events_emitted: 0,
  elapsed_time: 0,
  replay_speed: 1,
  target_flows_per_sec: null,
  actual_flows_per_sec: 0,
  last_event_time: null,
  error: null,
};

export function App() {
  // Sync tab with URL hash if present
  const getInitialTab = (): ActiveTab => {
    const hash = window.location.hash.replace('#', '');
    if (['overview', 'incidents', 'detectors', 'telemetry', 'replay', 'enclave', 'diagnostics'].includes(hash)) {
      return hash as ActiveTab;
    }
    const path = window.location.pathname.replace('/', '');
    if (path === 'alerts') return 'incidents';
    if (path === 'performance') return 'telemetry';
    if (path === 'architecture') return 'enclave';
    if (path === 'models') return 'detectors';
    return 'overview';
  };

  const [activeTab, setActiveTab] = useState<ActiveTab>(getInitialTab);
  const [status, setStatus] = useState<SystemStatus>(mockSystemStatus);
  const [metrics, setMetrics] = useState<IngestMetrics>(mockIngestMetrics);
  const [featureMetrics, setFeatureMetrics] = useState<FeatureMetrics>(mockFeatureMetrics);
  const [replay, setReplay] = useState<ReplayStatus>(initialReplay);
  const [sources, setSources] = useState<ReplaySource[]>(defaultReplaySources);
  const [latestFeature, setLatestFeature] = useState<FeatureVector | null>(mockFeatureVector);
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [detectorStatus, setDetectorStatus] = useState<DetectionStatus>(mockDetectionStatus);
  const [detectorResults, setDetectorResults] = useState<DetectorResult[]>([]);
  const [connected, setConnected] = useState(false);
  const [audioMuted, setAudioMuted] = useState(false);
  const [simulatedStreamActive, setSimulatedStreamActive] = useState(true);

  const socket = useRef<WebSocket | null>(null);

  // Tab change with hash update
  const handleTabChange = (tab: ActiveTab) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  // Initial API fetch & WebSocket connection
  useEffect(() => {
    // Attempt REST fetch from backend
    Promise.all([
      getSystemStatus(),
      getAlerts(),
      getReplaySources(),
      getDetectorStatus(),
      getDetectorResults(),
    ])
      .then(([nextStatus, nextAlerts, nextSources, nextDetectors, nextResults]) => {
        setStatus(nextStatus);
        if (nextAlerts.length > 0) setAlerts(nextAlerts);
        if (nextSources.length > 0) setSources(nextSources);
        setDetectorStatus(nextDetectors);
        setDetectorResults(nextResults);
      })
      .catch(() => {
        // Fallback to rich mock data if backend offline
      });

    // Setup WebSocket connection to Paladin backend
    let retryTimer: ReturnType<typeof setTimeout>;
    let attempts = 0;

    const connect = () => {
      const url = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace('http', 'ws') + '/ws/events';
      const ws = new WebSocket(url);
      socket.current = ws;

      ws.onopen = () => {
        attempts = 0;
        setConnected(true);
      };

      ws.onclose = () => {
        setConnected(false);
        retryTimer = setTimeout(connect, Math.min(1000 * 2 ** attempts++, 10000));
      };

      ws.onerror = () => ws.close();

      ws.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data) as { event_type: string; data?: unknown; payload?: unknown };
          const data = event.data ?? event.payload;

          if (event.event_type === 'INGEST_METRICS') {
            setMetrics(data as IngestMetrics);
          }
          if (event.event_type === 'REPLAY_STATUS') {
            setReplay(data as ReplayStatus);
          }
          if (event.event_type === 'FEATURE_METRICS') {
            setFeatureMetrics(data as FeatureMetrics);
            void getRecentFeatures().then((vectors) => {
              if (vectors[0]) setLatestFeature(vectors[0]);
            });
          }
          if (event.event_type === 'DETECTION_RESULT') {
            setDetectorResults((curr) => [data as DetectorResult, ...curr].slice(0, 100));
          }
          if (event.event_type === 'ALERT_CREATED') {
            const newAlert = data as Alert;
            setAlerts((curr) => [newAlert, ...curr.filter((item) => item.alert_id !== newAlert.alert_id)].slice(0, 500));
            if (!audioMuted) {
              playAlertChime(newAlert.severity);
            }
          }
          if (event.event_type === 'ALERT_UPDATED') {
            const updated = data as Alert;
            setAlerts((curr) => curr.map((item) => (item.alert_id === updated.alert_id ? updated : item)));
            setSelectedAlert((curr) => (curr?.alert_id === updated.alert_id ? updated : curr));
          }
        } catch {
          // Ignore parse errors
        }
      };
    };

    connect();

    return () => {
      clearTimeout(retryTimer);
      socket.current?.close();
    };
  }, [audioMuted]);

  // Background simulation tick (for realistic live dashboard feel when presenting offline)
  useEffect(() => {
    if (!simulatedStreamActive || connected) return;

    const interval = setInterval(() => {
      setMetrics((prev) => {
        const noise = (Math.random() - 0.5) * 20;
        const newRate = Math.max(120, prev.flows_per_second + noise);
        return {
          ...prev,
          packets_seen: prev.packets_seen + Math.round(newRate * 3),
          flows_emitted: prev.flows_emitted + Math.round(newRate * 0.1),
          flows_per_second: parseFloat(newRate.toFixed(1)),
          throughput_mbps: parseFloat((newRate * 0.082).toFixed(2)),
          active_flows: Math.round(1400 + Math.sin(Date.now() / 5000) * 80),
        };
      });

      setFeatureMetrics((prev) => ({
        ...prev,
        feature_vectors_per_sec: parseFloat((metrics.flows_per_second * 0.98).toFixed(1)),
        feature_processing_latency_ms: parseFloat((0.7 + Math.random() * 0.4).toFixed(3)),
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [simulatedStreamActive, connected, metrics.flows_per_second]);

  // Acknowledge Incident Action
  const handleAcknowledge = async (alertId: string) => {
    try {
      const updated = await acknowledgeAlert(alertId);
      setAlerts((curr) => curr.map((item) => (item.alert_id === alertId ? updated : item)));
      if (selectedAlert?.alert_id === alertId) setSelectedAlert(updated);
    } catch {
      // Local optimistic update if backend is unreachable
      setAlerts((curr) =>
        curr.map((item) => (item.alert_id === alertId ? { ...item, status: 'ACKNOWLEDGED' } : item))
      );
      if (selectedAlert?.alert_id === alertId) {
        setSelectedAlert((curr) => (curr ? { ...curr, status: 'ACKNOWLEDGED' } : null));
      }
    }
  };

  // Resolve Incident Action
  const handleResolve = async (alertId: string) => {
    try {
      const updated = await resolveAlert(alertId);
      setAlerts((curr) => curr.map((item) => (item.alert_id === alertId ? updated : item)));
      if (selectedAlert?.alert_id === alertId) setSelectedAlert(updated);
    } catch {
      // Local optimistic update if backend is unreachable
      setAlerts((curr) =>
        curr.map((item) => (item.alert_id === alertId ? { ...item, status: 'RESOLVED' } : item))
      );
      if (selectedAlert?.alert_id === alertId) {
        setSelectedAlert((curr) => (curr ? { ...curr, status: 'RESOLVED' } : null));
      }
    }
  };

  // Quick Attack Inject Action
  const handleQuickInject = (type: string) => {
    const id = `alt-${Math.random().toString(36).substring(2, 7)}-${type}`;
    let newAlert: Alert;

    if (type === 'ddos') {
      newAlert = {
        alert_id: id,
        timestamp: new Date().toISOString(),
        flow_id: `flow-${Math.floor(Math.random() * 90000 + 10000)}-syn-burst`,
        threat_class: 'DDOS',
        severity: 'CRITICAL',
        confidence_score: 0.985,
        source_ip: '198.51.100.99',
        destination_ip: '10.0.1.15',
        protocol: 'TCP',
        evidence: {
          syn_burst_rate: 18400,
          syn_ack_skew: 0.001,
          entropy: 7.98,
          mitre: 'T1498 - Network Denial of Service',
        },
        detector: 'ddos_detector',
        detector_version: '1.2.0',
        model_version: 'xgb-ddos-v1',
        observation_window_ms: 5000,
        alert_type: 'DDOS_SYN_BURST',
        subtype: 'HIGH_RATE_FLOOD',
        scope: 'flow',
        replay_session_id: 'quick_inject_ddos',
        feature_schema_version: '1.0',
        created_at: new Date().toISOString(),
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 1,
        status: 'NEW',
        evidence_completeness: 0.99,
        correlation_id: null,
        why_flagged: 'Instant operator-injected SYN Flood attack: 18,400 SYN packets/sec detected targeting edge gateway port 443.',
      };
    } else if (type === 'c2') {
      newAlert = {
        alert_id: id,
        timestamp: new Date().toISOString(),
        flow_id: `flow-${Math.floor(Math.random() * 90000 + 10000)}-c2-beacon`,
        threat_class: 'C2_BEACON',
        severity: 'HIGH',
        confidence_score: 0.92,
        source_ip: '10.0.4.112',
        destination_ip: '198.51.100.80',
        protocol: 'TCP',
        evidence: {
          mean_iat_ms: 10002,
          jitter_variance: 18.2,
          mitre: 'T1071.001 - Web Protocols C2',
        },
        detector: 'c2_beacon_detector',
        detector_version: '1.1.0',
        model_version: 'rf-c2-v2',
        observation_window_ms: 60000,
        alert_type: 'PERIODIC_HEARTBEAT',
        subtype: 'LOW_JITTER',
        scope: 'source_destination_pair',
        replay_session_id: 'quick_inject_c2',
        feature_schema_version: '1.0',
        created_at: new Date().toISOString(),
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 12,
        status: 'NEW',
        evidence_completeness: 0.95,
        correlation_id: null,
        why_flagged: 'Periodic telemetry pattern: 12 consecutive outbound connections with strict 10s intervals and 18ms jitter.',
      };
    } else if (type === 'dns_tunnel') {
      newAlert = {
        alert_id: id,
        timestamp: new Date().toISOString(),
        flow_id: `flow-${Math.floor(Math.random() * 90000 + 10000)}-dns-tunnel`,
        threat_class: 'DGA_DNS_TUNNEL',
        severity: 'CRITICAL',
        confidence_score: 0.975,
        source_ip: '10.0.2.77',
        destination_ip: '8.8.8.8',
        protocol: 'UDP',
        evidence: {
          shannon_entropy: 4.92,
          subdomain_length: 74,
          mitre: 'T1071.004 - DNS Tunneling',
        },
        detector: 'dns_tunnel_detector',
        detector_version: '1.4.0',
        model_version: 'bayes-dga-v1',
        observation_window_ms: 10000,
        alert_type: 'DNS_COVERT_EXFIL',
        subtype: 'HIGH_ENTROPY_TXT',
        scope: 'source_ip',
        replay_session_id: 'quick_inject_dns',
        feature_schema_version: '1.0',
        created_at: new Date().toISOString(),
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 58,
        status: 'NEW',
        evidence_completeness: 0.98,
        correlation_id: null,
        why_flagged: 'High-entropy encoded DNS query labels with Shannon entropy 4.92 exfiltrating payload chunks via TXT records.',
      };
    } else if (type === 'recon') {
      newAlert = {
        alert_id: id,
        timestamp: new Date().toISOString(),
        flow_id: `flow-${Math.floor(Math.random() * 90000 + 10000)}-portscan`,
        threat_class: 'RECON',
        severity: 'MEDIUM',
        confidence_score: 0.88,
        source_ip: '192.168.1.45',
        destination_ip: '10.0.0.0/24',
        protocol: 'TCP',
        evidence: {
          ports_scanned: 250,
          rate_per_sec: 120,
          mitre: 'T1046 - Network Service Discovery',
        },
        detector: 'recon_detector',
        detector_version: '1.0.0',
        model_version: null,
        observation_window_ms: 15000,
        alert_type: 'HORIZONTAL_SCAN',
        subtype: 'PORT_SWEEP',
        scope: 'source_ip',
        replay_session_id: 'quick_inject_recon',
        feature_schema_version: '1.0',
        created_at: new Date().toISOString(),
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 45,
        status: 'NEW',
        evidence_completeness: 0.92,
        correlation_id: null,
        why_flagged: 'Horizontal network sweep detected: 250 unique destination ports targeted within 2 seconds.',
      };
    } else {
      newAlert = {
        alert_id: id,
        timestamp: new Date().toISOString(),
        flow_id: `flow-${Math.floor(Math.random() * 90000 + 10000)}-exfil`,
        threat_class: 'DATA_EXFILTRATION',
        severity: 'HIGH',
        confidence_score: 0.93,
        source_ip: '10.0.3.88',
        destination_ip: '198.51.100.22',
        protocol: 'TCP',
        evidence: {
          bytes_out_mb: 620,
          bytes_in_mb: 1.2,
          ratio: 516.0,
          mitre: 'T1041 - Exfiltration Over C2 Channel',
        },
        detector: 'exfiltration_detector',
        detector_version: '1.1.0',
        model_version: 'iso-forest-v1',
        observation_window_ms: 30000,
        alert_type: 'ASYMMETRIC_EGRESS',
        subtype: 'VOLUME_BURST',
        scope: 'flow',
        replay_session_id: 'quick_inject_exfil',
        feature_schema_version: '1.0',
        created_at: new Date().toISOString(),
        first_seen: new Date().toISOString(),
        last_seen: new Date().toISOString(),
        occurrence_count: 15,
        status: 'NEW',
        evidence_completeness: 0.96,
        correlation_id: null,
        why_flagged: 'Severe directional byte asymmetry: 620 MB egressed outbound with 516:1 upload-to-download ratio.',
      };
    }

    setAlerts((curr) => [newAlert, ...curr]);
    if (!audioMuted) {
      playAlertChime(newAlert.severity);
    }
  };

  const unresolvedAlertCount = alerts.filter((a) => a.status === 'NEW').length;

  return (
    <div className="app-shell">
      {/* Sleek Top Navigation */}
      <Navigation
        activeTab={activeTab}
        onTabChange={handleTabChange}
        unresolvedAlertCount={unresolvedAlertCount}
        connected={connected}
        audioMuted={audioMuted}
        onToggleAudio={() => setAudioMuted(!audioMuted)}
        simulatedStreamActive={simulatedStreamActive}
        onToggleSimulatedStream={() => setSimulatedStreamActive(!simulatedStreamActive)}
        onQuickInject={handleQuickInject}
      />

      {/* Hardware Invariant Posture Strip */}
      <div className="status-strip-bar">
        <div className="posture-invariants">
          <span className="invariant-item">
            <i>&#x25C9;</i> HARDWARE DIODE: <strong>AIR-GAPPED RX ONLY</strong>
          </span>
          <span className="invariant-item">
            <i>&#x25C9;</i> RETURN PATH: <strong>NON-EXISTENT (BLOCKED)</strong>
          </span>
          <span className="invariant-item">
            <i>&#x25C9;</i> ACTIVE PROBING: <strong>DISABLED</strong>
          </span>
          <span className="invariant-item">
            <i>&#x25C9;</i> PAYLOAD DECRYPTION: <strong>OFF (METADATA ONLY)</strong>
          </span>
          <span className="invariant-item">
            <i>&#x25C9;</i> MEMORY QUEUE: <strong>10,000 MAX BOUNDED</strong>
          </span>
        </div>

        <div style={{ color: 'var(--copper-primary)', fontWeight: 600 }}>
          ACTIVE ENCLAVE POSTURE: STRICT PASSIVE
        </div>
      </div>

      {/* Dynamic Tab Views */}
      <main>
        {activeTab === 'overview' && (
          <OverviewView
            status={status}
            metrics={metrics}
            featureMetrics={featureMetrics}
            detectorStatus={detectorStatus}
            alerts={alerts}
            onSelectAlert={(a) => {
              setSelectedAlert(a);
              handleTabChange('incidents');
            }}
            onNavigateTab={(tab) => handleTabChange(tab)}
          />
        )}

        {activeTab === 'incidents' && (
          <IncidentsView
            alerts={alerts}
            selectedAlert={selectedAlert}
            onSelectAlert={setSelectedAlert}
            onAcknowledge={handleAcknowledge}
            onResolve={handleResolve}
          />
        )}

        {activeTab === 'detectors' && (
          <DetectorsView
            status={detectorStatus}
            recentResults={detectorResults}
            onTriggerTestSignal={(threatClass) => {
              handleQuickInject(
                threatClass === 'DDOS'
                  ? 'ddos'
                  : threatClass === 'C2_BEACON'
                  ? 'c2'
                  : threatClass === 'DGA_DNS_TUNNEL'
                  ? 'dns_tunnel'
                  : threatClass === 'RECON'
                  ? 'recon'
                  : 'exfil'
              );
            }}
          />
        )}

        {activeTab === 'telemetry' && (
          <TrafficView
            metrics={metrics}
            featureMetrics={featureMetrics}
            latestVector={latestFeature}
          />
        )}

        {activeTab === 'replay' && (
          <ReplayWorkbench
            sources={sources}
            status={replay}
            onStatusChange={setReplay}
            onSimulateAttackScenario={(name) => {
              if (name.includes('ddos')) handleQuickInject('ddos');
              else if (name.includes('c2')) handleQuickInject('c2');
              else if (name.includes('recon')) handleQuickInject('recon');
              else if (name.includes('tunnel') || name.includes('dga')) handleQuickInject('dns_tunnel');
              else if (name.includes('exfil')) handleQuickInject('exfil');
              else handleQuickInject('ddos');
            }}
          />
        )}

        {activeTab === 'enclave' && <EnclaveArchitectureView status={status} />}

        {activeTab === 'diagnostics' && (
          <DiagnosticsView
            status={status}
            metrics={metrics}
            featureMetrics={featureMetrics}
          />
        )}
      </main>

      {/* Enterprise SOC Footer */}
      <footer className="app-footer">
        <div>
          <span><strong>PALADIN</strong> &bull; Passive Cyber-Threat Intelligence Enclave &bull; v1.0</span>
        </div>
        <div>
          <span>
            PHYSICAL OPTICAL DIODE &bull; ZERO RETURN PATH &bull; METADATA-ONLY THREAT CLASSIFICATION
          </span>
        </div>
      </footer>
    </div>
  );
}
