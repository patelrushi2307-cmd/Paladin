import { Panel } from './Panel';

const threats = ['DDoS', 'C2 beacon', 'DNS / DGA', 'Encrypted', 'Recon', 'Exfiltration'];
export function ThreatDistribution() {
  return <Panel title="Threat distribution" eyebrow="CLASSIFICATION"><div className="distribution"><div className="donut"><span>0<small>ALERTS</small></span></div><div className="legend">{threats.map((threat, index) => <div key={threat}><i className={`dot d${index}`} /><span>{threat}</span><strong>0</strong></div>)}</div></div></Panel>;
}
