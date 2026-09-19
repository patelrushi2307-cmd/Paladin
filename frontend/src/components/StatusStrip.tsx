import { Shield, Radio, Lock, Zap, ArrowRight, Activity, Terminal } from 'lucide-react';

export function StatusStrip() {
  return (
    <div className="system-subbar">
      <div className="invariant-items">
        <div className="invariant-item">
          <Shield size={14} className="val-active" />
          <span>Postured: <strong className="val-active">RECEIVE ONLY (Hardware Invariant)</strong></span>
        </div>
        <div className="invariant-item">
          <Radio size={14} className="val-passive" />
          <span>Return Path: <strong className="val-passive">PHYSICALLY ABSENT (Zero TX)</strong></span>
        </div>
        <div className="invariant-item">
          <Lock size={14} />
          <span>Payload Decryption: <strong>DISABLED (Metadata-Only)</strong></span>
        </div>
      </div>
      <div className="invariant-items">
        <div className="invariant-item">
          <Terminal size={14} />
          <span>Enclave Mode: <strong>PASSIVE_OBSERVER_V1</strong></span>
        </div>
      </div>
    </div>
  );
}
