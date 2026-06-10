import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { type ComponentType, type SVGProps } from 'react';

interface LucideProps extends SVGProps<SVGSVGElement> {
  size?: number | string;
}

interface CategoryCardProps {
  icon: ComponentType<LucideProps>;
  name: string;
  description: string;
  growthRate: number;
}

export default function CategoryCard({
  icon: Icon,
  name,
  description,
  growthRate,
}: CategoryCardProps) {
  const navigate = useNavigate();

  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => navigate(`/market-insight?category=${encodeURIComponent(name)}`)}
      className="glass-light cursor-pointer rounded-xl p-4 transition-colors hover:border-yiwu-500/30"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yiwu-500/10 text-yiwu-400">
          <Icon size={20} />
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            growthRate > 0
              ? 'bg-yiwu-500/10 text-yiwu-400'
              : 'bg-red-500/10 text-red-400'
          }`}
        >
          {growthRate > 0 ? '+' : ''}
          {growthRate}%
        </span>
      </div>
      <h3 className="text-sm font-medium text-white mb-1">{name}</h3>
      <p className="text-xs text-gray-500 line-clamp-2">{description}</p>
    </motion.div>
  );
}
