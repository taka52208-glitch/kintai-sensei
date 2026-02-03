import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  Tabs,
  Tab,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { settingsApi } from '../services/api';
import { useIsAdmin } from '../stores/authStore';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function SettingsPage() {
  const isAdmin = useIsAdmin();
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // 検知ルール設定
  const [rules, setRules] = useState({
    breakMinutes6h: 45,
    breakMinutes8h: 60,
    dailyWorkHoursAlert: 10,
    nightStartHour: 22,
    nightEndHour: 5,
  });

  // 検知ルール取得
  const { data: rulesData, isLoading: rulesLoading } = useQuery({
    queryKey: ['settings', 'rules'],
    queryFn: settingsApi.getRules,
  });

  useEffect(() => {
    if (rulesData) {
      setRules(rulesData);
    }
  }, [rulesData]);

  // 検知ルール保存
  const rulesMutation = useMutation({
    mutationFn: () => settingsApi.updateRules(rules),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'rules'] });
      setSuccess('検知ルールを保存しました');
      setError('');
    },
    onError: () => {
      setError('保存に失敗しました');
      setSuccess('');
    },
  });

  if (rulesLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            設定
          </Typography>

          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
              {success}
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
            <Tab label="検知ルール" />
            <Tab label="テンプレート" disabled={!isAdmin} />
            <Tab label="語彙辞書" disabled={!isAdmin} />
          </Tabs>

          {/* 検知ルール */}
          <TabPanel value={tabValue} index={0}>
            <Typography variant="subtitle2" gutterBottom>
              休憩ルール
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="6時間超勤務の必要休憩時間（分）"
                  type="number"
                  value={rules.breakMinutes6h}
                  onChange={(e) => setRules({ ...rules, breakMinutes6h: Number(e.target.value) })}
                  size="small"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="8時間超勤務の必要休憩時間（分）"
                  type="number"
                  value={rules.breakMinutes8h}
                  onChange={(e) => setRules({ ...rules, breakMinutes8h: Number(e.target.value) })}
                  size="small"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              長時間労働アラート
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="日次勤務時間アラート閾値（時間）"
                  type="number"
                  value={rules.dailyWorkHoursAlert}
                  onChange={(e) => setRules({ ...rules, dailyWorkHoursAlert: Number(e.target.value) })}
                  size="small"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              深夜帯定義
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="深夜開始時刻"
                  type="number"
                  value={rules.nightStartHour}
                  onChange={(e) => setRules({ ...rules, nightStartHour: Number(e.target.value) })}
                  size="small"
                  inputProps={{ min: 0, max: 23 }}
                  helperText="0〜23"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="深夜終了時刻"
                  type="number"
                  value={rules.nightEndHour}
                  onChange={(e) => setRules({ ...rules, nightEndHour: Number(e.target.value) })}
                  size="small"
                  inputProps={{ min: 0, max: 23 }}
                  helperText="0〜23"
                />
              </Grid>
            </Grid>

            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={() => rulesMutation.mutate()}
              disabled={rulesMutation.isPending}
            >
              保存
            </Button>
          </TabPanel>

          {/* テンプレート */}
          <TabPanel value={tabValue} index={1}>
            <Alert severity="info">
              テンプレート編集機能は管理者のみ利用可能です。
              是正理由文の3種類のテンプレートを編集できます。
            </Alert>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              ※ 詳細なテンプレート編集機能は今後実装予定です
            </Typography>
          </TabPanel>

          {/* 語彙辞書 */}
          <TabPanel value={tabValue} index={2}>
            <Alert severity="info">
              語彙辞書編集機能は管理者のみ利用可能です。
              「従業員」→「スタッフ」などの置換ルールを設定できます。
            </Alert>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              ※ 詳細な語彙辞書編集機能は今後実装予定です
            </Typography>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
