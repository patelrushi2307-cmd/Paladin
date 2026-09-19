import { useState } from 'react';
import type { ReplaySource, ReplayStatus } from '../types/ingest';
import { replayAction } from '../services/api';
import { Panel } from './Panel';

export function ReplayLab({ sources, status, onStatus }: { sources: ReplaySource[]; status: ReplayStatus; onStatus: (status: ReplayStatus) => void }) {
  const [selected, setSelected] = useState('');
  const [mode, setMode] = useState('realtime');
  const [busy, setBusy] = useState(false);
  const selectedSource = sources.find((source) => source.path === selected) ?? sources[0];
  async function action(name: 'start' | 'pause' | 'resume' | 'stop' | 'restart') {
  if (name === 'start' && !selectedSource) return;
  setBusy(true);
  try {
    const result = await replayAction(
      name,
      name === 'start'
        ? {
            source_type: selectedSource.source_type,
            source_path: selectedSource.path,
            mode,
            speed_multiplier: 1,
          }
        : undefined,
    );
    onStatus(result);
  } catch (err) {
    alert(`Replay ${name} failed: ${(err as Error).message}`);
  } finally {
    setBusy(false);
  }
}
  return <Panel title="Replay Lab" eyebrow="OFFLINE INPUT WORKBENCH"><div className="replay-form"><label>SOURCE<select value={selectedSource?.path ?? ''} onChange={(event) => setSelected(event.target.value)}><option value="">No source available</option>{sources.map((source) => <option key={source.path} value={source.path}>{source.name} / {source.source_type}</option>)}</select></label><label>MODE<select value={mode} onChange={(event) => setMode(event.target.value)}><option value="realtime">Real-time</option><option value="accelerated">Accelerated</option><option value="fixed_rate">Fixed flow rate</option></select></label></div><div className="replay-controls"><button disabled={busy || !selectedSource} onClick={() => void action('start')}>START</button><button disabled={busy || status.state !== 'RUNNING'} onClick={() => void action('pause')}>PAUSE</button><button disabled={busy || status.state !== 'PAUSED'} onClick={() => void action('resume')}>RESUME</button><button disabled={busy || ['IDLE', 'COMPLETED'].includes(status.state)} onClick={() => void action('stop')}>STOP</button></div><div className="replay-status"><span>STATUS <b>{status.state}</b></span><span>EMITTED <b>{status.events_emitted}</b></span><span>ACTUAL <b>{status.actual_flows_per_sec.toFixed(1)} flows/s</b></span></div><small className="replay-note">Offline parsing only. Replayed packets are never transmitted to a network interface.</small></Panel>;
}
