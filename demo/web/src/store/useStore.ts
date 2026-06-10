import { create } from 'zustand';

export const categories = [
  '日用百货',
  '饰品配件',
  '玩具',
  '文具办公用品',
  '针织品',
  '工艺品',
  '电子电器',
  '五金工具',
  '服装服饰',
  '家居装饰',
];

interface User {
  id: string;
  email: string;
  company: string;
  plan: string;
}

interface StoreState {
  categories: string[];
  selectedCategory: string;
  budget: string;
  targetMarket: string;
  isAuthenticated: boolean;
  user: User | null;
  selectedPolicyCity: string;
  setSelectedCategory: (category: string) => void;
  setBudget: (budget: string) => void;
  setTargetMarket: (market: string) => void;
  login: (user: User) => void;
  logout: () => void;
  setSelectedPolicyCity: (city: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  categories,
  selectedCategory: categories[0],
  budget: '中',
  targetMarket: '欧洲（义新欧班列直达）',
  isAuthenticated: false,
  user: null,
  selectedPolicyCity: '义乌',
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setBudget: (budget) => set({ budget }),
  setTargetMarket: (market) => set({ targetMarket: market }),
  login: (user) => set({ isAuthenticated: true, user }),
  logout: () => set({ isAuthenticated: false, user: null }),
  setSelectedPolicyCity: (city) => set({ selectedPolicyCity: city }),
}));
