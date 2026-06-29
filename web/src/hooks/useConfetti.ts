import { useCallback } from 'react';
import confetti from 'canvas-confetti';

export function useConfetti() {
  const burst = useCallback(() => {
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#7B2FBE', '#A855F7', '#F59E0B', '#FBBF24', '#34D399', '#FCD34D'],
      disableForReducedMotion: true,
    });
  }, []);

  const bigCelebration = useCallback(() => {
    const end = Date.now() + 600;
    const frame = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#7B2FBE', '#A855F7', '#F59E0B'],
        disableForReducedMotion: true,
      });
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#FBBF24', '#34D399', '#FCD34D'],
        disableForReducedMotion: true,
      });
      if (Date.now() < end) requestAnimationFrame(frame);
    };
    frame();
  }, []);

  return { burst, bigCelebration };
}
