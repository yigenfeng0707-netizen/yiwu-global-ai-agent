/**
 * 骨架屏加载组件 - 数据加载时的占位UI
 */
export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse rounded-xl border border-gray-700/50 bg-gray-800/50 p-6">
      <div className="mb-4 h-5 w-2/5 rounded bg-gray-700/60" />
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="mb-2 h-4 rounded bg-gray-700/40"
          style={{ width: `${60 + Math.random() * 30}%` }}
        />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="animate-pulse rounded-xl border border-gray-700/50 bg-gray-800/50 p-6">
      <div className="mb-4 h-5 w-1/3 rounded bg-gray-700/60" />
      <div className="flex items-end gap-2 h-40">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="flex-1 rounded-t bg-gray-700/40"
            style={{ height: `${30 + Math.random() * 70}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 4, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="animate-pulse rounded-xl border border-gray-700/50 bg-gray-800/50 p-6">
      <div className="mb-4 h-5 w-1/3 rounded bg-gray-700/60" />
      <div className="space-y-3">
        {/* Header */}
        <div className="flex gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <div key={i} className="h-4 flex-1 rounded bg-gray-700/60" />
          ))}
        </div>
        {/* Rows */}
        {Array.from({ length: rows }).map((_, ri) => (
          <div key={ri} className="flex gap-4">
            {Array.from({ length: cols }).map((_, ci) => (
              <div key={ci} className="h-4 flex-1 rounded bg-gray-700/30" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
