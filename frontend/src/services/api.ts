import type { Alert, SystemStatus } from '../types/contracts';
import type { FeatureVector, ReplaySource, ReplayStatus } from '../types/ingest';
import type { DetectionStatus, DetectorResult } from '../types/detector';

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_URL}/api/system/status`);
  if (!response.ok) throw new Error('System status unavailable');
  return response.json() as Promise<SystemStatus>;
}

export async function getAlerts(limit = 100): Promise<Alert[]> {
  const response = await fetch(`${API_URL}/api/alerts?limit=${limit}`);
  if (!response.ok) throw new Error('Alerts unavailable');
  return response.json() as Promise<Alert[]>;
}

export async function acknowledgeAlert(alertId: string): Promise<Alert> {
  const response = await fetch(`${API_URL}/api/alerts/${encodeURIComponent(alertId)}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error('Failed to acknowledge alert');
  return response.json() as Promise<Alert>;
}

export async function resolveAlert(alertId: string): Promise<Alert> {
  const response = await fetch(`${API_URL}/api/alerts/${encodeURIComponent(alertId)}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error('Failed to resolve alert');
  return response.json() as Promise<Alert>;
}

export async function getAlertSummary(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_URL}/api/alerts/summary`);
  if (!response.ok) throw new Error('Alert summary unavailable');
  return response.json() as Promise<Record<string, unknown>>;
}

export async function getRelatedAlerts(alertId: string): Promise<Alert[]> {
  const response = await fetch(`${API_URL}/api/alerts/${encodeURIComponent(alertId)}/related`);
  if (!response.ok) return [];
  return response.json() as Promise<Alert[]>;
}

export async function getReplaySources(): Promise<ReplaySource[]> {
  const response = await fetch(`${API_URL}/api/replay/sources`);
  if (!response.ok) throw new Error('Replay sources unavailable');
  return (await response.json()).sources as ReplaySource[];
}

export async function replayAction(
  action: 'start' | 'pause' | 'resume' | 'stop' | 'restart',
  body?: object
): Promise<ReplayStatus> {
  const response = await fetch(`${API_URL}/api/replay/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) throw new Error((await response.json()).detail ?? 'Replay action failed');
  return response.json() as Promise<ReplayStatus>;
}

export async function getRecentFeatures(): Promise<FeatureVector[]> {
  const response = await fetch(`${API_URL}/api/features/recent`);
  if (!response.ok) throw new Error('Features unavailable');
  return response.json() as Promise<FeatureVector[]>;
}

export async function getDetectorStatus(): Promise<DetectionStatus> {
  const response = await fetch(`${API_URL}/api/detectors/status`);
  if (!response.ok) throw new Error('Detector status unavailable');
  return response.json() as Promise<DetectionStatus>;
}

export async function getDetectorResults(): Promise<DetectorResult[]> {
  const response = await fetch(`${API_URL}/api/detectors/results/recent`);
  if (!response.ok) throw new Error('Detector results unavailable');
  return response.json() as Promise<DetectorResult[]>;
}
