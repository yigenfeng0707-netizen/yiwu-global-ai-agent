// P2-1: vitest 全局 setup —— 注册 @testing-library/jest-dom 自定义匹配器
// （toBeInTheDocument / toHaveTextContent 等），所有测试文件自动生效。
import '@testing-library/jest-dom/vitest';

// jsdom 的 localStorage 是 Proxy 实现，部分 vitest+jsdom 版本组合下其 get/set
// trap 对 getItem/setItem 表现异常（Home.tsx useState 初始化器调用时报
// "not a function"，而 Object.assign 修补又触发 "trap returned falsish"）。
// 此处用 Object.defineProperty 整体替换为纯对象 mock，绕开 Proxy 陷阱，
// 保证所有测试中 localStorage 行为一致可预测。
const store: Record<string, string> = {};
const localStorageMock: Storage = {
  getItem: (k: string) => (k in store ? store[k] : null),
  setItem: (k: string, v: string) => { store[k] = String(v); },
  removeItem: (k: string) => { delete store[k]; },
  clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
  get length() { return Object.keys(store).length; },
  key: (i: number) => Object.keys(store)[i] ?? null,
};
Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  writable: true,
  configurable: true,
});
