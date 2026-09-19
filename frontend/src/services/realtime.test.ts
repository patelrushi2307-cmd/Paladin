import { describe, expect, it } from 'vitest';
import { isRealtimeEventType } from './realtime';

describe('realtime event contract', () => {
  it('accepts all backend event families', () => {
    expect(isRealtimeEventType('SYSTEM_STATUS')).toBe(true);
    expect(isRealtimeEventType('ALERT_CREATED')).toBe(true);
    expect(isRealtimeEventType('ALERT_UPDATED')).toBe(true);
  });

  it('rejects malformed or unknown messages', () => {
    expect(isRealtimeEventType('not-an-event')).toBe(false);
    expect(isRealtimeEventType(null)).toBe(false);
  });
});
