import React from 'react';
import { 
  ShieldAlert, 
  Activity, 
  Radar, 
  Binary, 
  FlaskConical, 
  Cpu, 
  SlidersHorizontal, 
  Volume2, 
  VolumeX, 
  Zap
} from 'lucide-react';

export type ActiveTab = 'overview' | 'incidents' | 'detectors' | 'telemetry' | 'replay' | 'enclave' | 'diagnostics';

interface NavigationProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  unresolvedAlertCount: number;
  connected: boolean;
  audioMuted: boolean;
  onToggleAudio: () => void;
  simulatedStreamActive: boolean;
  onToggleSimulatedStream: () => void;
  onQuickInject: (type: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  onTabChange,
  unresolvedAlertCount,
  connected,
  audioMuted,
  onToggleAudio,
  simulatedStreamActive,
  onToggleSimulatedStream,
  onQuickInject,
}) => {
  return (
    <header className="topbar">
      {/* Brand */}
      <div className="brand-section" onClick={() => onTabChange('overview')} role="button" tabIndex={0}>
        <div className="brand-icon">
          <ShieldAlert size={22} />
        </div>
        <div className="brand-text">
          <h1>Paladin</h1>
          <p>PASSIVE THREAT DEFENSE ENCLAVE</p>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <nav className="nav-tabs" aria-label="Main Navigation">
        <button
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => onTabChange('overview')}
          title="Operations Matrix & Command"
        >
          <Activity size={15} />
          <span>Overview</span>
        </button>

        <button
          className={`nav-tab ${activeTab === 'incidents' ? 'active' : ''}`}
          onClick={() => onTabChange('incidents')}
          title="Security Incidents & Triage"
        >
          <Radar size={15} />
          <span>Incidents</span>
          {unresolvedAlertCount > 0 && (
            <span className="tab-badge">{unresolvedAlertCount}</span>
          )}
        </button>

        <button
          className={`nav-tab ${activeTab === 'detectors' ? 'active' : ''}`}
          onClick={() => onTabChange('detectors')}
          title="AI & Heuristic Threat Detectors"
        >
          <SlidersHorizontal size={15} />
          <span>Detectors</span>
        </button>

        <button
          className={`nav-tab ${activeTab === 'telemetry' ? 'active' : ''}`}
          onClick={() => onTabChange('telemetry')}
          title="Flow Telemetry & Feature Vectors"
        >
          <Binary size={15} />
          <span>Telemetry</span>
        </button>

        <button
          className={`nav-tab ${activeTab === 'replay' ? 'active' : ''}`}
          onClick={() => onTabChange('replay')}
          title="Attack Simulator & PCAP Replay Lab"
        >
          <FlaskConical size={15} />
          <span>Replay Lab</span>
        </button>

        <button
          className={`nav-tab ${activeTab === 'enclave' ? 'active' : ''}`}
          onClick={() => onTabChange('enclave')}
          title="Hardware Data Diode Invariants"
        >
          <Cpu size={15} />
          <span>Enclave</span>
        </button>
      </nav>

      {/* Status & Quick Action Controls */}
      <div className="top-actions">
        {/* Optical Link Status */}
        <div className="enclave-badge" title="Physical Unidirectional Data Diode Boundary">
          <span className="pulse-dot" />
          <span>{connected ? 'LINK: LIVE' : simulatedStreamActive ? 'STREAM: DEMO' : 'LINK: STANDBY'}</span>
        </div>

        {/* Audio Mute Toggle */}
        <button
          className={`action-btn ${!audioMuted ? 'active' : ''}`}
          onClick={onToggleAudio}
          title={audioMuted ? 'Unmute Threat Audio Chimes' : 'Mute Threat Audio Chimes'}
        >
          {audioMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
        </button>

        {/* Simulated Telemetry Stream Toggle */}
        <button
          className={`action-btn ${simulatedStreamActive ? 'active' : ''}`}
          onClick={onToggleSimulatedStream}
          title="Toggle Background Synthetic Flow Stream"
        >
          <Zap size={15} />
          <span>{simulatedStreamActive ? 'Sim Running' : 'Sim Paused'}</span>
        </button>

        {/* Quick Attack Inject */}
        <select
          aria-label="Quick Inject Attack"
          className="action-btn"
          onChange={(e) => {
            if (e.target.value) {
              onQuickInject(e.target.value);
              e.target.value = '';
            }
          }}
          defaultValue=""
        >
          <option value="" disabled>⚡ Inject Attack...</option>
          <option value="ddos">SYN Flood DDoS</option>
          <option value="c2">C2 Periodic Beacon</option>
          <option value="dns_tunnel">DNS Covert Tunnel</option>
          <option value="recon">Horizontal Port Recon</option>
          <option value="exfil">Asymmetric Exfil</option>
        </select>
      </div>
    </header>
  );
};
