export const realtimeEventTypes = ['SYSTEM_STATUS', 'INGEST_METRICS', 'REPLAY_STATUS', 'FEATURE_METRICS', 'DETECTION_RESULT', 'ALERT_CREATED', 'ALERT_UPDATED'] as const;
export type RealtimeEventType = typeof realtimeEventTypes[number];

export function isRealtimeEventType(value: unknown): value is RealtimeEventType {
  return typeof value === 'string' && (realtimeEventTypes as readonly string[]).includes(value);
}
