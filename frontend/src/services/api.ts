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

// レスポンスインターセプター（エラーハンドリング）
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // 401エラー時の処理
    if (error.response?.status === 401) {
      // リフレッシュトークンでの再取得を試みる（今後実装）
      // 失敗したらログアウト
      useAuthStore.getState().clearAuth();
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

// ========================================
// 認証API
// ========================================

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  logout: async () => {
    await api.post('/api/auth/logout');
  },

  refresh: async () => {
    const response = await api.post('/api/auth/refresh');
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
