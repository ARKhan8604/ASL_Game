/**
 * Train/inference feature parity: the browser's clipToSequence() MUST match ml/dataset.py
 * exactly, or the trained model degrades silently. The golden file seq_coffee_correct.json
 * was produced by ml.dataset.clip_to_sequence on the same fixture; if this test fails, the
 * TS and Python feature extractors have diverged — fix before trusting any model.
 */
import { describe, it, expect } from 'vitest';
import { frameFromDict } from '../src/engine/landmarks';
import { clipToSequence, SEQ_LEN, FEAT_DIM } from '../src/engine/sequenceFeatures';

import coffeeCorrect from './fixtures/coffee_correct.json';
import golden from './fixtures/seq_coffee_correct.json';

describe('feature parity (TS clipToSequence vs Python ml/dataset.py)', () => {
  const frames = coffeeCorrect.frames.map((fd) =>
    frameFromDict(fd as Parameters<typeof frameFromDict>[0])
  );
  const seq = clipToSequence(frames);

  it('produces a sequence', () => {
    expect(seq).not.toBeNull();
  });

  it('matches the golden shape', () => {
    expect(seq!.length).toBe(SEQ_LEN);
    expect(seq![0].length).toBe(FEAT_DIM);
    expect(golden.seq_len).toBe(SEQ_LEN);
    expect(golden.feat_dim).toBe(FEAT_DIM);
  });

  it('matches the Python output element-wise', () => {
    let maxDiff = 0;
    for (let t = 0; t < SEQ_LEN; t++) {
      for (let j = 0; j < FEAT_DIM; j++) {
        maxDiff = Math.max(maxDiff, Math.abs(seq![t][j] - golden.data[t][j]));
      }
    }
    expect(maxDiff).toBeLessThan(1e-5);
  });
});
