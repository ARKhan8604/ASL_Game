import { motion } from 'framer-motion';

interface Props {
  lessonTitle: string;
  current: number;
  total: number;
  onClose: () => void;
}

export function LessonHeader({ lessonTitle: _lessonTitle, current, total, onClose }: Props) {
  const progress = current / total;

  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <button
        onClick={onClose}
        className="w-8 h-8 flex items-center justify-center text-z-gray-400 hover:text-white transition-colors"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>

      <div className="flex-1">
        <div className="h-3 bg-z-surface rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #7B2FBE, #A855F7)' }}
            initial={{ width: 0 }}
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      <span className="text-xs font-semibold text-z-gray-300 tracking-wide">
        {current}/{total}
      </span>
    </div>
  );
}
