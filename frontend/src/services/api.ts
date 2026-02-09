import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { config } from '../config';
import { useAuthStore } from '../stores/authStore';

// Axiosインスタンス作成
export const api = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（トークン付与）
api.interceptors.request.use(
  (requestConfig: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken && requestConfig.headers) {
      requestConfig.headers.Authorization = `Bearer ${accessToken}`;
    }
    return requestConfig;
  },
  (error) => Promise.reject(error)
);

// リフレッシュ中フラグ（多重リフレッシュ防止）
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

// レスポンスインターセプター（エラーハンドリング）
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    const requestUrl = originalRequest?.url || '';

    // 401エラー時の処理（認証API以外）
    if (
      error.response?.status === 401 &&
      !requestUrl.includes('/auth/login') &&
      !requestUrl.includes('/auth/refresh')
    ) {
      const { refreshToken } = useAuthStore.getState();

      if (refreshToken && originalRequest) {
        // リフレッシュ試行
        if (!isRefreshing) {
          isRefreshing = true;
          try {
            const response = await api.post('/api/auth/refresh', {
              refresh_token: refreshToken,
            });
            const newAccessToken = response.data.access_token;
            useAuthStore.getState().setAccessToken(newAccessToken);
            isRefreshing = false;
            onRefreshed(newAccessToken);
            // 元のリクエストをリトライ
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(originalRequest);
          } catch {
            isRefreshing = false;
            refreshSubscribers = [];
            useAuthStore.getState().clearAuth();
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
          }
        } else {
          // 他のリクエストはリフレッシュ完了を待つ
          return new Promise((resolve) => {
            refreshSubscribers.push((token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(api(originalRequest));
            });
          });
        }
      } else {
        // リフレッシュトークンなし→ログアウト
        useAuthStore.getState().clearAuth();
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

// ========================================
// ヘルスチェック（コールドスタート対策）
// ========================================

export const healthApi = {
  ping: async () => {
    try {
      await api.get('/api/health', { timeout: 60000 });
    } catch {
      // ウォームアップ目的なのでエラーは無視
    }
  },
};

// ========================================
// 認証API
// ========================================

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  signup: async (data: {
    organization_name: string;
    name: string;
    email: string;
    password: string;
  }) => {
    const response = await api.post('/api/auth/signup', data);
    return response.data;
  },

  logout: async () => {
    const { accessToken, refreshToken } = useAuthStore.getState();
    await api.post('/api/auth/logout', {
      access_token: accessToken,
      refresh_token: refreshToken,
    });
  },

  refresh: async (refreshToken: string) => {
    const response = await api.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.put('/api/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// ========================================
// ユーザーAPI
// ========================================

export const usersApi = {
  list: async (params?: { page?: number; pageSize?: number }) => {
    const response = await api.get('/api/users', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(`/api/users/${id}`);
    return response.data;
  },

  invite: async (data: { email: string; role: string; storeId?: string }) => {
    const response = await api.post('/api/users/invite', data);
    return response.data;
  },

  update: async (id: string, data: { role?: string; storeId?: string; isActive?: boolean }) => {
    const response = await api.put(`/api/users/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/users/${id}`);
  },
};

// ========================================
// 店舗API
// ========================================

export const storesApi = {
  list: async () => {
    const response = await api.get('/api/stores');
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(`/api/stores/${id}`);
    return response.data;
  },

  create: async (data: { code: string; name: string }) => {
    const response = await api.post('/api/stores', data);
    return response.data;
  },

  update: async (id: string, data: { code?: string; name?: string }) => {
    const response = await api.put(`/api/stores/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/stores/${id}`);
  },
};

// ========================================
// 勤怠データAPI
// ========================================

export const attendanceApi = {
  preview: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/attendance/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  upload: async (file: File, storeId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('store_id', storeId);
    const response = await api.post('/api/attendance/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// ========================================
// 異常API
// ========================================

export const issuesApi = {
  list: async (params?: {
    page?: number;
    pageSize?: number;
    storeId?: string;
    employeeId?: string;
    type?: string;
    severity?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
  }) => {
    const response = await api.get('/api/issues', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(`/api/issues/${id}`);
    return response.data;
  },

  updateStatus: async (id: string, status: string) => {
    const response = await api.put(`/api/issues/${id}`, { status });
    return response.data;
  },

  addLog: async (id: string, data: { action: string; memo?: string }) => {
    const response = await api.post(`/api/issues/${id}/logs`, data);
    return response.data;
  },

  generateReason: async (id: string, data: {
    templateType: string;
    causeCategory: string;
    causeDetail?: string;
    actionTaken: string;
    prevention: string;
  }) => {
    const response = await api.post(`/api/issues/${id}/reason`, data);
    return response.data;
  },
};

// ========================================
// レポートAPI
// ========================================

export const reportsApi = {
  generate: async (data: {
    storeId?: string;
    month: string; // YYYY-MM
    format: 'pdf' | 'csv';
    maskPersonalInfo?: boolean;
  }) => {
    const response = await api.post('/api/reports', data, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// ========================================
// 課金API
// ========================================

export const billingApi = {
  getPlan: async () => {
    const response = await api.get('/api/billing/plan');
    return response.data;
  },

  createCheckout: async (data: { price_id: string; quantity: number }) => {
    const response = await api.post('/api/billing/checkout', data);
    return response.data;
  },

  openPortal: async () => {
    const response = await api.post('/api/billing/portal');
    return response.data;
  },
};

// ========================================
// 設定API
// ========================================

export const settingsApi = {
  getRules: async () => {
    const response = await api.get('/api/settings/rules');
    return response.data;
  },

  updateRules: async (data: Record<string, unknown>) => {
    const response = await api.put('/api/settings/rules', data);
    return response.data;
  },

  getTemplates: async () => {
    const response = await api.get('/api/settings/templates');
    return response.data;
  },

  updateTemplates: async (data: Record<string, unknown>) => {
    const response = await api.put('/api/settings/templates', data);
    return response.data;
  },

  getDictionary: async () => {
    const response = await api.get('/api/settings/dictionary');
    return response.data;
  },

  updateDictionary: async (data: Record<string, string>) => {
    const response = await api.put('/api/settings/dictionary', data);
    return response.data;
  },
};
