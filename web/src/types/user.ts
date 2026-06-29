export interface UserProgress {
  xp: number;
  level: number;
  streak: number;
  lastPracticeDate: string | null;
  streakFreezes: number;
  dailyGoalMinutes: number;
  dailyProgressMinutes: number;
  completedLessons: string[];
  signAccuracy: Record<string, SignStats>;
  achievements: string[];
}

export interface SignStats {
  attempts: number;
  successes: number;
  lastAttempt: number;
  nextReviewAt: number;
  interval: number;
  easeFactor: number;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt?: number;
}
