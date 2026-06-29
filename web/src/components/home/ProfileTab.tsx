import { useUserStore } from '@/stores/useUserStore';
import { motion } from 'framer-motion';

export function ProfileTab() {
  const { xp, level, streak, completedLessons, signAccuracy } = useUserStore();
  const totalSigns = Object.keys(signAccuracy).length;
  const masteredSigns = Object.values(signAccuracy).filter(
    (s) => s.successes >= 3 && s.successes / s.attempts >= 0.7
  ).length;

  const stats = [
    { label: 'Total XP', value: xp, icon: '✨', color: 'text-z-yellow' },
    { label: 'Level', value: level, icon: '🏆', color: 'text-z-orange' },
    { label: 'Streak', value: `${streak}d`, icon: '🔥', color: 'text-z-orange-bright' },
    { label: 'Completed', value: completedLessons.length, icon: '📖', color: 'text-z-purple-light' },
  ];

  return (
    <div className="px-4 pb-24">
      <motion.div
        className="text-center mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-z-purple to-z-purple-deep flex items-center justify-center text-5xl mx-auto mb-3 shadow-lg shadow-z-purple/30">
          🤟
        </div>
        <h2 className="text-2xl font-bold tracking-tight">Your Stats</h2>
        <p className="text-z-gray-300 text-sm mt-1">
          {masteredSigns > 0
            ? `${masteredSigns} of ${totalSigns} signs mastered`
            : 'Start signing to track progress'}
        </p>
      </motion.div>

      <div className="grid grid-cols-2 gap-3 mb-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            className="bg-z-card border border-white/5 rounded-2xl p-4 text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.06 }}
          >
            <span className="text-2xl">{stat.icon}</span>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>
              {stat.value}
            </p>
            <p className="text-[11px] text-z-gray-400 mt-0.5 tracking-wide">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="bg-z-card border border-white/5 rounded-2xl p-5"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="font-bold text-base mb-3 tracking-wide">This Week</h3>
        <div className="flex justify-between">
          {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, i) => {
            const dayOfWeek = new Date().getDay();
            const adjustedDay = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
            const isToday = i === adjustedDay;
            const isPast = i < adjustedDay;
            return (
              <div key={i} className="flex flex-col items-center gap-1.5">
                <span className="text-[10px] text-z-gray-400 font-semibold">{day}</span>
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold ${
                  isToday
                    ? 'bg-z-purple text-white shadow-md shadow-z-purple/40'
                    : isPast
                      ? 'bg-z-surface text-z-gray-300'
                      : 'bg-transparent text-z-gray-500 border border-z-gray-500/20'
                }`}>
                  {isPast ? '✓' : isToday ? '●' : ''}
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
