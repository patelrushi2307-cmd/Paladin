import type { Alert } from '../types/contracts';
import { Panel } from './Panel';

export function AlertTable({ alerts }: { alerts: Alert[] }) {
  return <Panel title="Live alert table" eyebrow="ALERT STREAM" className="alert-panel"><div className="table-wrap"><table><thead><tr><th>TIME</th><th>THREAT CLASS</th><th>SEVERITY</th><th>SOURCE</th><th>CONFIDENCE</th></tr></thead><tbody>{alerts.length === 0 ? <tr><td colSpan={5} className="empty-state"><span className="empty-glyph">--</span><strong>No alerts observed</strong><small>Alerts will appear here when detectors are connected.</small></td></tr> : alerts.map((alert) => <tr key={alert.alert_id}><td>{new Date(alert.timestamp).toLocaleTimeString()}</td><td>{alert.threat_class}</td><td><span className={`severity ${alert.severity.toLowerCase()}`}>{alert.severity}</span></td><td>{alert.source_ip}</td><td>{Math.round(alert.confidence_score * 100)}%</td></tr>)}</tbody></table></div></Panel>;
}
