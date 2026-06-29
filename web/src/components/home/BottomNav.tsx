import { motion } from 'framer-motion';

type Tab = 'learn' | 'review' | 'profile';

interface Props {
  active: Tab;
  onChange: (tab: Tab) => void;
}

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: 'learn', label: 'Journey', icon: '🗺️' },
  { id: 'review', label: 'Review', icon: '🪞' },
  { id: 'profile', label: 'Me', icon: '🤟' },
];

export function BottomNav({ active, onChange }: Props) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-z-bg/90 backdrop-blur-md border-t border-z-purple-deep/40">
      <div className="max-w-lg mx-auto flex items-center justify-around py-2.5">
        {tabs.map((tab) => {
          const isActive = active === tab.id;
          return (
            <motion.button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={`relative flex flex-col items-center gap-1 px-5 py-1.5 rounded-2xl transition-all ${
                isActive ? 'bg-z-purple/20' : ''
              }`}
              whileTap={{ scale: 0.9 }}
            >
              <span className={`text-xl transition-transform ${isActive ? 'scale-110' : ''}`}>
                {tab.icon}
              </span>
              <span className={`text-[11px] font-semibold tracking-wide ${
                isActive ? 'text-z-purple-glow' : 'text-z-gray-400'
              }`}>
                {tab.label}
              </span>
              {isActive && (
                <motion.div
                  className="absolute -bottom-1 h-[3px] w-6 bg-z-purple-light rounded-full"
                  layoutId="nav-dot"
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
