import { describe, it, expect } from 'vitest';
import { gatePass, gateHint, type ClassifierVote } from '../src/engine/gate';

const vote = (perSign: Record<string, number>): ClassifierVote => {
  const top = Object.entries(perSign).sort((a, b) => b[1] - a[1])[0];
  return { topSign: top[0], confidence: top[1], perSign };
};

describe('gatePass', () => {
  it('rule failure is never rescued by the classifier', () => {
    expect(gatePass(false, vote({ COFFEE: 0.99 }), 'COFFEE')).toBe(false);
  });

  it('classifier disabled (no vote) -> rules alone (back-compat)', () => {
    expect(gatePass(true, null, 'COFFEE')).toBe(true);
  });

  it('rule pass + confident model agreement -> pass', () => {
    expect(gatePass(true, vote({ COFFEE: 0.9, TEA: 0.1 }), 'COFFEE')).toBe(true);
  });

  it('THE KEY CASE: rule pass but model says a different sign -> vetoed', () => {
    // The classic confusor: loose rules accept it, but the model recognizes TEA.
    expect(gatePass(true, vote({ TEA: 0.85, COFFEE: 0.1 }), 'COFFEE')).toBe(false);
  });

  it('respects the confidence threshold', () => {
    expect(gatePass(true, vote({ COFFEE: 0.4 }), 'COFFEE', 0.5)).toBe(false);
    expect(gatePass(true, vote({ COFFEE: 0.6 }), 'COFFEE', 0.5)).toBe(true);
  });
});

describe('gateHint', () => {
  it('no hint when classifier disabled', () => {
    expect(gateHint(null, 'COFFEE')).toBeNull();
  });

  it('no hint when model agrees with the prompt', () => {
    expect(gateHint(vote({ COFFEE: 0.9 }), 'COFFEE')).toBeNull();
  });

  it('hints toward the confidently-detected different sign', () => {
    const h = gateHint(vote({ THANK_YOU: 0.8, COFFEE: 0.1 }), 'COFFEE');
    expect(h).toContain('THANK YOU');
  });
});
