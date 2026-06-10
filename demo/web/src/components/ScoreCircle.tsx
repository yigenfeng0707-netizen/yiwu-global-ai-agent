import { motion } from 'framer-motion';

interface ScoreCircleProps {
  score: number;
  level?: string;
  size?: number;
  strokeWidth?: number;
}

export default function ScoreCircle({
  score,
  level,
  size = 120,
  strokeWidth = 8,
}: ScoreCircleProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = score >= 70 ? '#D4272C' : score >= 50 ? '#D4A853' : '#ef4444';
  const displayLevel = level || (score >= 80 ? '优秀' : score >= 70 ? '良好' : score >= 50 ? '一般' : '较差');

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={strokeWidth} />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color}
          strokeWidth={strokeWidth} strokeLinecap="round" strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-2xl font-bold" style={{ color }}>{score}</span>
        <span className="text-xs text-gray-400">{displayLevel}</span>
      </div>
    </div>
  );
}
