import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { TopBar } from '@/components/shared/TopBar';
import { StreakCard } from '@/components/home/StreakCard';
import { LessonTree } from '@/components/home/LessonTree';
import { BottomNav } from '@/components/home/BottomNav';
import { PracticeTab } from '@/components/home/PracticeTab';
import { ProfileTab } from '@/components/home/ProfileTab';

type Tab = 'learn' | 'review' | 'profile';

interface Props {
  onStartLesson: (id: string) => void;
  onStartPractice: () => void;
  onStartStory: (id: string) => void;
}

export function HomePage({ onStartLesson, onStartPractice, onStartStory }: Props) {
  const [tab, setTab] = useState<Tab>('learn');

  return (
    <div className="min-h-screen bg-z-bg">
      <TopBar />

      <div className="max-w-lg mx-auto px-4 pt-4">
        <AnimatePresence mode="wait">
          {tab === 'learn' && (
            <motion.div
              key="learn"
              initial={{ opacity: 0, x: -15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 15 }}
              transition={{ duration: 0.2 }}
            >
              <StreakCard />
              <LessonTree onSelectLesson={(id) => {
                if (id === 'coffee-story') {
                  onStartStory(id);
                } else {
                  onStartLesson(id);
                }
              }} />
            </motion.div>
          )}

          {tab === 'review' && (
            <motion.div
              key="review"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              transition={{ duration: 0.2 }}
            >
              <PracticeTab onStartPractice={onStartPractice} onStartStory={() => onStartStory('coffee-story')} />
            </motion.div>
          )}

          {tab === 'profile' && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              transition={{ duration: 0.2 }}
            >
              <ProfileTab />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <BottomNav active={tab} onChange={setTab} />
    </div>
  );
}
