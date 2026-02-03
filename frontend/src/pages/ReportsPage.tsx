import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import { reportsApi } from '../services/api';

export default function ReportsPage() {
  const [form, setForm] = useState({
    month: new Date().toISOString().slice(0, 7), // YYYY-MM
    format: 'pdf' as 'pdf' | 'csv',
    maskPersonalInfo: false,
  });

  const [error, setError] = useState('');

  const reportMutation = useMutation({
    mutationFn: () => reportsApi.generate(form),
    onSuccess: (blob) => {
      // ダウンロード処理
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `kintai-report-${form.month}.${form.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setError('');
    },
    onError: () => {
      setError('レポートの生成に失敗しました');
    },
  });

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            月次レポート生成
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="対象月"
                type="month"
                value={form.month}
                onChange={(e) => setForm({ ...form, month: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                select
                fullWidth
                label="出力形式"
                value={form.format}
                onChange={(e) => setForm({ ...form, format: e.target.value as 'pdf' | 'csv' })}
              >
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={form.maskPersonalInfo}
                    onChange={(e) => setForm({ ...form, maskPersonalInfo: e.target.checked })}
                  />
                }
                label="個人情報をマスクする（監査提出用）"
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Button
                variant="contained"
                startIcon={reportMutation.isPending ? <CircularProgress size={20} /> : <DownloadIcon />}
                onClick={() => reportMutation.mutate()}
                disabled={reportMutation.isPending}
              >
                レポートをダウンロード
              </Button>
            </Grid>
          </Grid>

          <Box mt={4}>
            <Typography variant="subtitle2" gutterBottom>
              レポート内容
            </Typography>
            <Typography variant="body2" color="text.secondary">
              - 異常件数サマリー（種別別、店舗別）
            </Typography>
            <Typography variant="body2" color="text.secondary">
              - 対応状況（完了/未完了）
            </Typography>
            <Typography variant="body2" color="text.secondary">
              - 個票一覧（是正理由文を含む）
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
