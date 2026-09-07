import { create } from 'zustand';

/**
 * 全局数据来源状态：真实后端 / 演示数据降级
 * api.ts 中每次请求成功标记 live，降级到 mockData 时标记 demo。
 */
export type DataSourceMode = 'unknown' | 'live' | 'demo';

interface DataSourceState {
  mode: DataSourceMode;
  lastError?: string;
  markLive: () => void;
  markDemo: (reason?: string) => void;
}

export const useDataSource = create<DataSourceState>((set) => ({
  mode: 'unknown',
  markLive: () => set({ mode: 'live', lastError: undefined }),
  markDemo: (reason) => set({ mode: 'demo', lastError: reason }),
}));

/** api.ts 内部使用：成功/降级统一打点 */
export function withSource<T>(request: Promise<T>, fallback: () => T): Promise<T> {
  const { markLive, markDemo } = useDataSource.getState();
  return request.then(
    (value) => {
      markLive();
      return value;
    },
    (err) => {
      markDemo(String(err?.message || err));
      return fallback();
    },
  );
}
