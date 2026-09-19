import type { DetectionStatus, DetectorResult } from '../types/detector';
import { Panel } from './Panel';

const labels: Record<string, string> = { ddos: 'DDoS', recon: 'Recon', c2: 'C2 Beacon', exfiltration: 'Data Exfiltration', dga_dns: 'DGA / DNS Tunnel', encrypted_malware: 'Encrypted Malware' };
export function DetectorPanel({ status, results }: { status: DetectionStatus; results: DetectorResult[] }) {
  const latest = results[0];
  return <Panel title="Detection engine" eyebrow="OBSERVATION ANALYTICS"><div className="detector-list">{status.detectors.map((detector) => <div key={detector.name}><span className="detector-dot" /> <strong>{labels[detector.name] ?? detector.name}</strong><b>{detector.status}</b></div>)}</div>{latest ? <div className="detector-result"><span className="eyebrow">LATEST DETECTOR RESULT / NOT AN ALERT</span><strong>{labels[latest.detector] ?? latest.detector} <em>{latest.subtype ?? latest.threat_class}</em></strong><div><span>Detection score <b>{latest.score.toFixed(3)}</b></span><span>Scope <b>{latest.scope}</b></span><span>Applicability <b>{latest.applicability}</b></span></div><small>{latest.reasons.join(' / ') || 'No supporting reasons'}</small></div> : <div className="details-empty"><strong>No detector results observed</strong><small>Results will appear after FeatureVectors enter the engine.</small></div>}</Panel>;
}
