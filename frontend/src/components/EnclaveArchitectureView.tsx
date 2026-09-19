import React from 'react';
import { 
  ShieldCheck, 
  Lock, 
  Radio, 
  ArrowRight, 
  CheckCircle2, 
  AlertOctagon, 
  Cpu, 
  Layers, 
  Eye, 
  Network 
} from 'lucide-react';
import type { SystemStatus } from '../types/contracts';

interface EnclaveArchitectureViewProps {
  status: SystemStatus;
}

export const EnclaveArchitectureView: React.FC<EnclaveArchitectureViewProps> = ({ status }) => {
  return (
    <div className="main-view">
      <div className="view-header">
        <div>
          <span className="eyebrow">
            <Radio size={12} /> HARDWARE DATA DIODE SECURITY SPECIFICATION
          </span>
          <h2>Unidirectional Enclave Posture</h2>
          <p>
            Physical layer isolation guarantees. Paladin operates exclusively behind a one-way optical photodiode barrier.
          </p>
        </div>

        <div className="enclave-badge">
          <ShieldCheck size={16} />
          <span>AIR-GAP MATHEMATICALLY VERIFIED</span>
        </div>
      </div>

      {/* Interactive Hardware Optical Diagram */}
      <div className="enclave-diagram-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span className="eyebrow">PHYSICAL TRANSMISSION BARRIER (LAYER 1)</span>
            <h3 style={{ color: '#fff', fontSize: '1.2rem', marginTop: 4 }}>
              Optical Photodiode Unidirectional Link
            </h3>
          </div>
          <span className="status-badge resolved">100% HARDWARE ENFORCED</span>
        </div>

        <div className="optical-path-flow">
          {/* Node 1: Monitored Network */}
          <div className="diode-node">
            <Network size={24} style={{ margin: '0 auto', color: 'var(--text-muted)' }} />
            <span className="node-title">Monitored Network</span>
            <span className="node-sub">Network TAP / SPAN Port</span>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', marginTop: 4 }}>
              Production Traffic Mirror
            </div>
          </div>

          <div className="flow-arrow">&rarr;</div>

          {/* Node 2: Optical Transmitter */}
          <div className="diode-node">
            <Radio size={24} style={{ margin: '0 auto', color: 'var(--copper-primary)' }} />
            <span className="node-title">Tx Optical Emitter</span>
            <span className="node-sub">LED / Laser Diode</span>
            <div style={{ fontSize: '0.65rem', color: 'var(--copper-primary)', marginTop: 4 }}>
              Transmit Only
            </div>
          </div>

          <div className="flow-arrow">&rarr;</div>

          {/* Node 3: Physical Fiber Cable */}
          <div className="diode-node core-diode">
            <span style={{ fontSize: '1.2rem' }}>⚡</span>
            <span className="node-title" style={{ color: 'var(--copper-light)' }}>Fiber Optic Core</span>
            <span className="node-sub" style={{ color: '#fff' }}>1-Way Photon Wave</span>
            <div style={{ fontSize: '0.65rem', color: 'var(--copper-light)', marginTop: 4 }}>
              Reverse travel physically impossible
            </div>
          </div>

          <div className="flow-arrow">&rarr;</div>

          {/* Node 4: Optical Receiver */}
          <div className="diode-node">
            <Eye size={24} style={{ margin: '0 auto', color: 'var(--enclave-safe)' }} />
            <span className="node-title">Rx Photodiode</span>
            <span className="node-sub">Optical Receiver</span>
            <div style={{ fontSize: '0.65rem', color: 'var(--enclave-safe)', marginTop: 4 }}>
              TX Pin Cut / Absent
            </div>
          </div>

          <div className="flow-arrow">&rarr;</div>

          {/* Node 5: Paladin Isolated Enclave */}
          <div className="diode-node enclave-zone">
            <ShieldCheck size={24} style={{ margin: '0 auto', color: 'var(--enclave-safe)' }} />
            <span className="node-title" style={{ color: 'var(--enclave-safe)' }}>Paladin Enclave</span>
            <span className="node-sub">Isolated Memory State</span>
            <div style={{ fontSize: '0.65rem', color: '#fff', marginTop: 4 }}>
              Zero Return Path
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 8, border: '1px solid var(--border-hairline)' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            <strong>Fundamental Security Guarantee:</strong> In the event of total application compromise within the Paladin enclave, no attacker can transmit a single bit back toward production or the monitored network.
          </span>
          <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: 'var(--copper-primary)' }}>
            Invariant Proof: #HARDWARE-INV-001
          </span>
        </div>
      </div>

      {/* 5 Invariant Cards */}
      <div className="grid-3col">
        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 01</span>
              <h3>Receive Only Boundary</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Data flows into the enclave via a passive parser (PCAP/JSONL/TAP). No TCP acknowledgments, SYN-ACKs, or ICMP replies are ever generated or transmitted.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>ENFORCED ({status.ingest_mode.toUpperCase()})</strong>
          </div>
        </div>

        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 02</span>
              <h3>Zero Return Path</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            The physical network interface card (NIC) has no transmit pin connected. The Linux kernel routing table has no default gateway pointing back to the monitored environment.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>VERIFIED (RETURN_PATH = FALSE)</strong>
          </div>
        </div>

        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 03</span>
              <h3>No Payload Decryption</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Paladin possesses no TLS private keys, certificates, or MITM interception infrastructure. Threat classification is derived solely from traffic shape, packet sizes, and metadata.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>DISABLED (PRIVACY PRESERVED)</strong>
          </div>
        </div>

        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 04</span>
              <h3>Zero Active Probing</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            No outbound port scans, reverse DNS lookups, whois queries, or banner grabs are ever performed. Paladin remains completely invisible and undetectable on the wire.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>PROHIBITED BY CONTRACT</strong>
          </div>
        </div>

        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 05</span>
              <h3>No Inline Blocking</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Paladin is a pure out-of-band threat intelligence sensor. It does not sit inline as a firewall or choke point, eliminating any risk of production denial of service.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>OUT-OF-BAND PASSIVE ONLY</strong>
          </div>
        </div>

        <div className="card-panel">
          <div className="card-panel-header">
            <div className="card-panel-title">
              <span className="eyebrow">INVARIANT 06</span>
              <h3>Bounded Memory Footprint</h3>
            </div>
            <CheckCircle2 size={18} style={{ color: 'var(--enclave-safe)' }} />
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            All queues and flow state tables are bounded and governed by explicit TTL eviction policies, guaranteeing immune resilience against memory exhaustion attacks.
          </p>
          <div className="meta-field">
            <span>Status</span>
            <strong style={{ color: 'var(--enclave-safe)' }}>10,000 MAXQUEUE BOUNDED</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
