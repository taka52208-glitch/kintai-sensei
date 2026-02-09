// 環境変数の集約モジュール
// process.envはここ経由でのみアクセス

export const config = {
  // API - 本番ではVercel rewritesを使用するため空文字
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8634'),

  // アプリ設定
  appName: '勤怠チェック',
  appVersion: '1.0.0',

  // 認証
  tokenKey: 'kintai_access_token',
  refreshTokenKey: 'kintai_refresh_token',
  tokenExpiry: 60 * 60 * 1000, // 1時間

  // Google Analytics
  gaId: import.meta.env.VITE_GA_ID || '',

  // ページネーション
  defaultPageSize: 20,

  // 検知ルールのデフォルト値
  defaultRules: {
    breakMinutes6h: 45,  // 6時間超勤務の休憩
    breakMinutes8h: 60,  // 8時間超勤務の休憩
    dailyWorkHoursAlert: 10, // 日次アラート閾値
    nightStartHour: 22,  // 深夜開始
    nightEndHour: 5,     // 深夜終了
  },
} as const;

export type Config = typeof config;
