import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Divider,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { issuesApi } from '../services/api';
import type {
  Issue,
  IssueStatus,
  ReasonTemplateType,
  CauseCategory,
  ActionType,
  PreventionType,
} from '../types';
import {
  ISSUE_TYPE_LABELS,
  STATUS_LABELS,
  SEVERITY_LABELS,
  CAUSE_CATEGORY_LABELS,
  ACTION_TYPE_LABELS,
  PREVENTION_TYPE_LABELS,
} from '../types';

const TEMPLATE_TYPE_LABELS: Record<ReasonTemplateType, string> = {
  internal: '社内記録用',
  employee: '本人確認用',
  audit: '監査向け',
};

export default function IssueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 是正理由フォーム状態
  const [reasonForm, setReasonForm] = useState({
    templateType: 'internal' as ReasonTemplateType,
    causeCategory: 'forgot_clock' as CauseCategory,
    causeDetail: '',
    actionTaken: 'correction_request' as ActionType,
    prevention: 'operation_notice' as PreventionType,
  });

  // 生成された理由文
  const [generatedReason, setGeneratedReason] = useState('');
  const [copied, setCopied] = useState(false);

  // 対応ログフォーム
  const [logMemo, setLogMemo] = useState('');

  // 異常詳細取得
  const { data: issue, isLoading } = useQuery({
    queryKey: ['issue', id],
    queryFn: () => issuesApi.get(id!),
    enabled: !!id,
  });

  // ステータス更新
  const statusMutation = useMutation({
    mutationFn: (status: IssueStatus) => issuesApi.updateStatus(id!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue', id] });
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  // 対応ログ追加
  const logMutation = useMutation({
    mutationFn: (memo: string) => issuesApi.addLog(id!, { action: 'memo', memo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issue', id] });
      setLogMemo('');
    },
  });

  // 是正理由文生成
  const reasonMutation = useMutation({
    mutationFn: () => issuesApi.generateReason(id!, reasonForm),
    onSuccess: (data) => {
      setGeneratedReason(data.generatedText);
    },
  });

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedReason);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // フォールバック: 旧ブラウザ/権限不足時
      const textarea = document.createElement('textarea');
      textarea.value = generatedReason;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (!issue) {
    return (
      <Alert severity="error">
        異常データが見つかりません
      </Alert>
    );
  }

  const typedIssue = issue as Issue;

  return (
    <Box>
      {/* ヘッダー */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/dashboard')} sx={{ mr: 1 }}>
          <BackIcon />
        </IconButton>
        <Typography variant="h5">
          異常詳細
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 左カラム: 根拠 & 対応ログ */}
        <Grid size={{ xs: 12, md: 6 }}>
          {/* 根拠セクション */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                検知根拠
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">日付</Typography>
                  <Typography>{typedIssue.date}</Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">従業員</Typography>
                  <Typography>{typedIssue.employeeName}</Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">店舗</Typography>
                  <Typography>{typedIssue.storeName}</Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">異常種別</Typography>
                  <Typography>
                    <Chip
                      label={ISSUE_TYPE_LABELS[typedIssue.type]}
                      size="small"
                      variant="outlined"
                    />
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">重要度</Typography>
                  <Typography>
                    <Chip label={SEVERITY_LABELS[typedIssue.severity]} size="small" />
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Typography variant="caption" color="text.secondary">ステータス</Typography>
                  <Typography>
                    <Chip label={STATUS_LABELS[typedIssue.status]} size="small" />
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                適用ルール
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="body2">
                  {typedIssue.ruleDescription}
                </Typography>
              </Paper>

              {typedIssue.attendanceRecord && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    勤怠データ
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Grid container spacing={1}>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">出勤</Typography>
                        <Typography>{typedIssue.attendanceRecord.clockIn || '---'}</Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">退勤</Typography>
                        <Typography>{typedIssue.attendanceRecord.clockOut || '---'}</Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">休憩</Typography>
                        <Typography>
                          {typedIssue.attendanceRecord.breakMinutes !== null
                            ? `${typedIssue.attendanceRecord.breakMinutes}分`
                            : '---'}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" color="text.secondary">勤務区分</Typography>
                        <Typography>{typedIssue.attendanceRecord.workType || '---'}</Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </>
              )}
            </CardContent>
          </Card>

          {/* ステータス変更 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ステータス変更
              </Typography>
              <Box display="flex" gap={1}>
                {(['pending', 'in_progress', 'completed'] as IssueStatus[]).map((status) => (
                  <Button
                    key={status}
                    variant={typedIssue.status === status ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => statusMutation.mutate(status)}
                    disabled={statusMutation.isPending}
                  >
                    {STATUS_LABELS[status]}
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* 対応ログ */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                対応ログ
              </Typography>
              <Box display="flex" gap={1} mb={2}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="対応メモを入力..."
                  value={logMemo}
                  onChange={(e) => setLogMemo(e.target.value)}
                />
                <Button
                  variant="contained"
                  onClick={() => logMutation.mutate(logMemo)}
                  disabled={!logMemo || logMutation.isPending}
                >
                  追加
                </Button>
              </Box>
              <List dense>
                {typedIssue.logs?.map((log) => (
                  <ListItem key={log.id} divider>
                    <ListItemText
                      primary={log.memo || log.action}
                      secondary={`${log.userName} - ${new Date(log.createdAt).toLocaleString('ja-JP')}`}
                    />
                  </ListItem>
                ))}
                {(!typedIssue.logs || typedIssue.logs.length === 0) && (
                  <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                    対応ログがありません
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* 右カラム: 是正理由文生成 */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                是正理由文生成
              </Typography>

              <Grid container spacing={2}>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    select
                    fullWidth
                    label="出力種別"
                    value={reasonForm.templateType}
                    onChange={(e) => setReasonForm({ ...reasonForm, templateType: e.target.value as ReasonTemplateType })}
                    size="small"
                  >
                    {Object.entries(TEMPLATE_TYPE_LABELS).map(([value, label]) => (
                      <MenuItem key={value} value={value}>{label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    select
                    fullWidth
                    label="原因カテゴリ"
                    value={reasonForm.causeCategory}
                    onChange={(e) => setReasonForm({ ...reasonForm, causeCategory: e.target.value as CauseCategory })}
                    size="small"
                  >
                    {Object.entries(CAUSE_CATEGORY_LABELS).map(([value, label]) => (
                      <MenuItem key={value} value={value}>{label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="原因詳細（任意）"
                    value={reasonForm.causeDetail}
                    onChange={(e) => setReasonForm({ ...reasonForm, causeDetail: e.target.value })}
                    size="small"
                    multiline
                    rows={2}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    select
                    fullWidth
                    label="対応"
                    value={reasonForm.actionTaken}
                    onChange={(e) => setReasonForm({ ...reasonForm, actionTaken: e.target.value as ActionType })}
                    size="small"
                  >
                    {Object.entries(ACTION_TYPE_LABELS).map(([value, label]) => (
                      <MenuItem key={value} value={value}>{label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    select
                    fullWidth
                    label="再発防止"
                    value={reasonForm.prevention}
                    onChange={(e) => setReasonForm({ ...reasonForm, prevention: e.target.value as PreventionType })}
                    size="small"
                  >
                    {Object.entries(PREVENTION_TYPE_LABELS).map(([value, label]) => (
                      <MenuItem key={value} value={value}>{label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => reasonMutation.mutate()}
                    disabled={reasonMutation.isPending}
                  >
                    {reasonMutation.isPending ? <CircularProgress size={24} /> : '理由文を生成'}
                  </Button>
                </Grid>
              </Grid>

              {generatedReason && (
                <Box mt={3}>
                  <Divider sx={{ mb: 2 }} />
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="subtitle2">
                      生成結果
                    </Typography>
                    <IconButton size="small" onClick={handleCopy}>
                      {copied ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Box>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {generatedReason}
                    </Typography>
                  </Paper>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
