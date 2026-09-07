import { Zap, ClipboardList, CircleDashed } from 'lucide-react';
import { useDataSource } from '@/store/useDataSource';

/**
 * 全局数据来源徽章：顶栏实时展示当前数据是真实后端（含 AI）还是演示数据降级。
 * 评委/用户一眼可辨，避免 mock 降级被误认为真实能力。
 */
export default function DataSourceBadge() {
  const { mode } = useDataSource();

  if (mode === 'live') {
    return (
      <span
        className="flex items-center gap-1.5 rounded-full border border-yiwu-500/30 bg-yiwu-500/10 px-2.5 py-0.5 text-xs text-yiwu-400"
        title="后端 API + AI 大模型实时返回"
      >
        <Zap size={12} />
        实时数据 · AI 已接入
      </span>
    );
  }

  if (mode === 'demo') {
    return (
      <span
        className="flex items-center gap-1.5 rounded-full border border-gold-500/30 bg-gold-500/10 px-2.5 py-0.5 text-xs text-gold-400"
        title="后端不可达，当前展示本地演示数据（非实时结果）"
      >
        <ClipboardList size={12} />
        演示数据（后端不可达）
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2.5 py-0.5 text-xs text-gray-500">
      <CircleDashed size={12} />
      数据源待检测
    </span>
  );
}
