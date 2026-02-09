import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { issuesApi, attendanceApi, billingApi, storesApi } from '../services/api';
import { trackEvent } from '../utils/analytics';
import type { Issue, IssueType, IssueStatus, IssueSeverity } from '../types';
import { ISSUE_TYPE_LABELS, STATUS_LABELS, SEVERITY_LABELS } from '../types';

const SEVERITY_COLORS: Record<IssueSeverity, 'error' | 'warning' | 'info'> = {
  high: 'error',
  medium: 'warning',
  low: 'info',
};

const STATUS_COLORS: Record<IssueStatus, 'default' | 'primary' | 'success'> = {
  pending: 'default',
  in_progress: 'primary',
  completed: 'success',
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // フィルター状態
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
    type: '',
  });

  // ページネーション状態
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  // ファイルアップロード状態
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [selectedStoreId, setSelectedStoreId] = useState('');

  // プラン情報
  const { data: planData } = useQuery({
    queryKey: ['billing', 'plan'],
    queryFn: billingApi.getPlan,
  });

  // 店舗一覧取得（CSV upload用）
  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storesApi.list(),
  });

  // 異常一覧取得（ページネーション対応）
  const { data: issuesData, isLoading, refetch } = useQuery({
    queryKey: ['issues', filters, page, rowsPerPage],
    queryFn: () => issuesApi.list({
      page: page + 1,
      pageSize: rowsPerPage,
      status: filters.status || undefined,
      severity: filters.severity || undefined,
      type: filters.type || undefined,
    }),
  });

  // CSVアップロード
  const uploadMutation = useMutation({
    mutationFn: (file: File) => attendanceApi.upload(file, selectedStoreId),
    onSuccess: (data) => {
      let msg = `${data.record_count}件の勤怠データを取り込み、${data.issue_count}件の異常を検知しました`;
      if (data.skip_count > 0) {
        msg += `（${data.skip_count}件は既存データのためスキップ）`;
      }
      setUploadSuccess(msg);
      setUploadError('');
      queryClient.invalidateQueries({ queryKey: ['issues'] });
      trackEvent('csv_upload', { records: data.record_count, issues: data.issue_count });
    },
    onError: () => {
      setUploadError('ファイルの取り込みに失敗しました');
      setUploadSuccess('');
    },
  });

  // ドラッグ&ドロップ
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadError('');
      setUploadSuccess('');
      uploadMutation.mutate(acceptedFiles[0]);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
  });

  const issues: Issue[] = issuesData?.items || [];

  const usagePercent = planData
    ? Math.round((planData.employee_count / planData.employee_limit) * 100)
    : 0;

  return (
    <Box>
      {/* プラン使用状況バナー */}
      {planData && usagePercent >= 80 && (
        <Alert
          severity={usagePercent >= 100 ? 'error' : 'warning'}
          sx={{ mb: 3 }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => navigate('/settings?billing=upgrade')}
            >
              アップグレード
            </Button>
          }
        >
          従業員数: {planData.employee_count}/{planData.employee_limit}名
          {usagePercent >= 100
            ? '（上限に達しています。新規従業員の追加にはプランのアップグレードが必要です）'
            : '（まもなく上限に達します）'}
        </Alert>
      )}

      {/* CSVアップロードエリア */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            勤怠データ取り込み
          </Typography>
          {/* 店舗選択 */}
          {storesData?.items && storesData.items.length > 0 && (
            <TextField
              select
              fullWidth
              label="取り込み先店舗"
              value={selectedStoreId}
              onChange={(e) => setSelectedStoreId(e.target.value)}
              size="small"
              sx={{ mb: 2 }}
              helperText="未選択の場合、デフォルト店舗に割り当てられます"
            >
              <MenuItem value="">指定なし（デフォルト）</MenuItem>
              {storesData.items.map((store: { id: string; name: string; code: string }) => (
                <MenuItem key={store.id} value={store.id}>
                  {store.name}（{store.code}）
                </MenuItem>
              ))}
            </TextField>
          )}
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'action.hover',
              },
            }}
          >
            <input {...getInputProps()} />
            {uploadMutation.isPending ? (
              <CircularProgress />
            ) : (
              <>
                <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                <Typography>
                  {isDragActive
                    ? 'ファイルをドロップしてください'
                    : 'CSVファイルをドラッグ&ドロップ、またはクリックして選択'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  対応フォーマット: ジョブカン、Airシフト、汎用CSV
                </Typography>
              </>
            )}
          </Box>
          {uploadError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {uploadError}
            </Alert>
          )}
          {uploadSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {uploadSuccess}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* フィルター */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 3 }}>
              <TextField
                select
                fullWidth
                label="ステータス"
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                size="small"
              >
                <MenuItem value="">すべて</MenuItem>
                {Object.entries(STATUS_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <TextField
                select
                fullWidth
                label="重要度"
                value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                size="small"
              >
                <MenuItem value="">すべて</MenuItem>
                {Object.entries(SEVERITY_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <TextField
                select
                fullWidth
                label="異常種別"
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                size="small"
              >
                <MenuItem value="">すべて</MenuItem>
                {Object.entries(ISSUE_TYPE_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
              >
                更新
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 異常一覧 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            異常一覧
            {issuesData?.total !== undefined && (
              <Typography component="span" variant="body2" color="text.secondary" ml={1}>
                ({issuesData.total}件)
              </Typography>
            )}
          </Typography>

          {isLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : issues.length === 0 ? (
            <Box textAlign="center" p={4}>
              <Typography color="text.secondary">
                異常データがありません
              </Typography>
            </Box>
          ) : (
            <>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>日付</TableCell>
                    <TableCell>従業員</TableCell>
                    <TableCell>店舗</TableCell>
                    <TableCell>異常種別</TableCell>
                    <TableCell>重要度</TableCell>
                    <TableCell>ステータス</TableCell>
                    <TableCell align="center">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {issues.map((issue) => (
                    <TableRow key={issue.id} hover>
                      <TableCell>{issue.date}</TableCell>
                      <TableCell>{issue.employeeName}</TableCell>
                      <TableCell>{issue.storeName}</TableCell>
                      <TableCell>
                        <Chip
                          label={ISSUE_TYPE_LABELS[issue.type as IssueType]}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={SEVERITY_LABELS[issue.severity as IssueSeverity]}
                          size="small"
                          color={SEVERITY_COLORS[issue.severity as IssueSeverity]}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={STATUS_LABELS[issue.status as IssueStatus]}
                          size="small"
                          color={STATUS_COLORS[issue.status as IssueStatus]}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="詳細を見る">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/issues/${issue.id}`)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={issuesData?.total || 0}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[10, 20, 50]}
              labelRowsPerPage="表示件数:"
              labelDisplayedRows={({ from, to, count }) =>
                `${from}-${to} / ${count !== -1 ? count : `${to}+`}件`
              }
            />
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
