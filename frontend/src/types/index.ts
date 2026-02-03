// ========================================
// 共通型定義
// backend/src/schemas/ と同期すること
// ========================================

// ユーザーロール
export type UserRole = 'admin' | 'store_manager' | 'viewer';

// 異常種別
export type IssueType =
  | 'missing_clock_in'
  | 'missing_clock_out'
  | 'insufficient_break'
  | 'overtime'
  | 'night_work'
  | 'inconsistency';

// 異常の重要度
export type IssueSeverity = 'high' | 'medium' | 'low';

// 対応ステータス
export type IssueStatus = 'pending' | 'in_progress' | 'completed';

// 是正理由文の種別
export type ReasonTemplateType = 'internal' | 'employee' | 'audit';

// 原因カテゴリ
export type CauseCategory =
  | 'forgot_clock'
  | 'device_issue'
  | 'work_reason'
  | 'application_missing'
  | 'other';

// 対応種別
export type ActionType =
  | 'correction_request'
  | 'employee_confirmation'
  | 'overtime_application'
  | 'warning'
  | 'announcement';

// 再発防止種別
export type PreventionType =
  | 'operation_notice'
  | 'device_placement'
  | 'checklist'
  | 'double_check';

// ========================================
// エンティティ型
// ========================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  storeId: string | null;
  storeName: string | null;
  isActive: boolean;
  createdAt: string;
}

export interface Store {
  id: string;
  code: string;
  name: string;
  createdAt: string;
}

export interface Employee {
  id: string;
  employeeCode: string;
  name: string;
  storeId: string;
  storeName: string;
}

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  date: string;
  clockIn: string | null;
  clockOut: string | null;
  breakMinutes: number | null;
  workType: string | null;
  importedAt: string;
}

export interface Issue {
  id: string;
  attendanceRecordId: string;
  employeeId: string;
  employeeName: string;
  storeId: string;
  storeName: string;
  date: string;
  type: IssueType;
  severity: IssueSeverity;
  status: IssueStatus;
  ruleDescription: string;
  detectedAt: string;
  // 関連データ
  attendanceRecord?: AttendanceRecord;
  logs?: IssueLog[];
}

export interface IssueLog {
  id: string;
  issueId: string;
  userId: string;
  userName: string;
  action: string;
  memo: string | null;
  createdAt: string;
}

export interface CorrectionReason {
  id: string;
  issueId: string;
  templateType: ReasonTemplateType;
  causeCategory: CauseCategory;
  causeDetail: string | null;
  actionTaken: ActionType;
  prevention: PreventionType;
  generatedText: string;
  createdBy: string;
  createdAt: string;
}

// ========================================
// API リクエスト/レスポンス型
// ========================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: UserRole;
    store_id: string | null;
    store_name: string | null;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface IssueFilter {
  storeId?: string;
  employeeId?: string;
  type?: IssueType;
  severity?: IssueSeverity;
  status?: IssueStatus;
  dateFrom?: string;
  dateTo?: string;
}

export interface GenerateReasonRequest {
  templateType: ReasonTemplateType;
  causeCategory: CauseCategory;
  causeDetail?: string;
  actionTaken: ActionType;
  prevention: PreventionType;
}

export interface GenerateReasonResponse {
  generatedText: string;
  correctionReasonId: string;
}

// ========================================
// フォーム型
// ========================================

export interface IssueLogForm {
  action: string;
  memo?: string;
}

// ========================================
// 表示用ラベル
// ========================================

export const ISSUE_TYPE_LABELS: Record<IssueType, string> = {
  missing_clock_in: '出勤打刻漏れ',
  missing_clock_out: '退勤打刻漏れ',
  insufficient_break: '休憩不足',
  overtime: '長時間労働',
  night_work: '深夜勤務',
  inconsistency: '不整合',
};

export const SEVERITY_LABELS: Record<IssueSeverity, string> = {
  high: '高',
  medium: '中',
  low: '低',
};

export const STATUS_LABELS: Record<IssueStatus, string> = {
  pending: '未対応',
  in_progress: '対応中',
  completed: '完了',
};

export const CAUSE_CATEGORY_LABELS: Record<CauseCategory, string> = {
  forgot_clock: '打刻忘れ',
  device_issue: '端末不具合',
  work_reason: '業務都合',
  application_missing: '申請漏れ',
  other: 'その他',
};

export const ACTION_TYPE_LABELS: Record<ActionType, string> = {
  correction_request: '修正依頼',
  employee_confirmation: '本人確認',
  overtime_application: '残業申請',
  warning: '注意喚起',
  announcement: '周知',
};

export const PREVENTION_TYPE_LABELS: Record<PreventionType, string> = {
  operation_notice: '運用周知',
  device_placement: '端末配置見直し',
  checklist: 'チェックリスト導入',
  double_check: 'ダブルチェック体制',
};
