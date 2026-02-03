import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';
import { config } from '../config';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setAuth: (user: User, accessToken: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,

      setAuth: (user, accessToken) => {
        set({
          user,
          accessToken,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: config.tokenKey,
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Rehydration完了後にisLoadingをfalseに
        if (state) {
          state.setLoading(false);
        }
      },
    }
  )
);

// 権限チェックヘルパー
export const useIsAdmin = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'admin';
};

export const useIsStoreManager = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'admin' || user?.role === 'store_manager';
};

export const useCanEdit = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role !== 'viewer';
};
