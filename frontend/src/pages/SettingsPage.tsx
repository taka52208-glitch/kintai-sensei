import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
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
  Chip,
  Stack,
} from '@mui/material';
import {
  Save as SaveIcon,
  CreditCard as CreditCardIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { settingsApi, billingApi } from '../services/api';
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

const PLAN_LABELS: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' }> = {
  free: { label: 'Free', color: 'default' },
  standard: { label: 'Standard', color: 'primary' },
  pro: { label: 'Pro', color: 'secondary' },
};

export default function SettingsPage() {
  const isAdmin = useIsAdmin();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const [tabValue, setTabValue] = useState(0);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  // Stripe決済結果のフィードバック
  useEffect(() => {
    const billing = searchParams.get('billing');
    if (billing === 'success') {
      setSuccess('プランの変更が完了しました');
      setTabValue(3); // 課金タブへ
    } else if (billing === 'cancel') {
      setError('プラン変更がキャンセルされました');
      setTabValue(3);
    }
  }, [searchParams]);

  // プラン情報取得
  const { data: planData, isLoading: planLoading } = useQuery({
    queryKey: ['billing', 'plan'],
    queryFn: billingApi.getPlan,
  });

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
            <Tab label="プラン・課金" disabled={!isAdmin} />
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

          {/* プラン・課金 */}
          <TabPanel value={tabValue} index={3}>
            {planLoading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : planData ? (
              <Box>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight={700}>
                    現在のプラン
                  </Typography>
                  <Chip
                    label={PLAN_LABELS[planData.plan]?.label || planData.plan}
                    color={PLAN_LABELS[planData.plan]?.color || 'default'}
                    size="small"
                  />
                </Stack>

                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          従業員数
                        </Typography>
                        <Typography variant="h5">
                          {planData.employee_count} / {planData.employee_limit}名
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  プラン一覧
                </Typography>

                <Grid container spacing={2} sx={{ mb: 3 }}>
                  {/* Free */}
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Card variant="outlined" sx={{
                      borderColor: planData.plan === 'free' ? 'primary.main' : undefined,
                      borderWidth: planData.plan === 'free' ? 2 : 1,
                    }}>
                      <CardContent>
                        <Typography variant="h6">Free</Typography>
                        <Typography variant="h4" fontWeight={700}>¥0</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          10名まで・基本機能
                        </Typography>
                        {planData.plan === 'free' && (
                          <Chip icon={<CheckCircleIcon />} label="現在のプラン" color="primary" size="small" />
                        )}
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Standard */}
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Card variant="outlined" sx={{
                      borderColor: planData.plan === 'standard' ? 'primary.main' : undefined,
                      borderWidth: planData.plan === 'standard' ? 2 : 1,
                    }}>
                      <CardContent>
                        <Typography variant="h6">Standard</Typography>
                        <Typography variant="h4" fontWeight={700}>¥300<Typography component="span" variant="body2">/人月</Typography></Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          50名まで・全機能
                        </Typography>
                        {planData.plan === 'standard' ? (
                          <Chip icon={<CheckCircleIcon />} label="現在のプラン" color="primary" size="small" />
                        ) : planData.plan === 'free' ? (
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={checkoutLoading ? <CircularProgress size={16} /> : <CreditCardIcon />}
                            disabled={checkoutLoading}
                            onClick={async () => {
                              setCheckoutLoading(true);
                              try {
                                const { checkout_url } = await billingApi.createCheckout({
                                  price_id: 'STRIPE_PRICE_STANDARD',
                                  quantity: 1,
                                });
                                window.location.href = checkout_url;
                              } catch {
                                setError('チェックアウトの作成に失敗しました');
                                setCheckoutLoading(false);
                              }
                            }}
                          >
                            アップグレード
                          </Button>
                        ) : null}
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Pro */}
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Card variant="outlined" sx={{
                      borderColor: planData.plan === 'pro' ? 'primary.main' : undefined,
                      borderWidth: planData.plan === 'pro' ? 2 : 1,
                    }}>
                      <CardContent>
                        <Typography variant="h6">Pro</Typography>
                        <Typography variant="h4" fontWeight={700}>¥500<Typography component="span" variant="body2">/人月</Typography></Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          無制限・優先サポート
                        </Typography>
                        {planData.plan === 'pro' ? (
                          <Chip icon={<CheckCircleIcon />} label="現在のプラン" color="secondary" size="small" />
                        ) : (
                          <Button
                            variant="contained"
                            color="secondary"
                            size="small"
                            startIcon={checkoutLoading ? <CircularProgress size={16} /> : <CreditCardIcon />}
                            disabled={checkoutLoading}
                            onClick={async () => {
                              setCheckoutLoading(true);
                              try {
                                const { checkout_url } = await billingApi.createCheckout({
                                  price_id: 'STRIPE_PRICE_PRO',
                                  quantity: 1,
                                });
                                window.location.href = checkout_url;
                              } catch {
                                setError('チェックアウトの作成に失敗しました');
                                setCheckoutLoading(false);
                              }
                            }}
                          >
                            アップグレード
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* カスタマーポータル */}
                {planData.stripe_subscription_id && (
                  <Box>
                    <Divider sx={{ my: 3 }} />
                    <Button
                      variant="outlined"
                      startIcon={<CreditCardIcon />}
                      onClick={async () => {
                        try {
                          const { portal_url } = await billingApi.openPortal();
                          window.location.href = portal_url;
                        } catch {
                          setError('ポータルの表示に失敗しました');
                        }
                      }}
                    >
                      請求情報・支払い方法の管理
                    </Button>
                  </Box>
                )}
              </Box>
            ) : (
              <Alert severity="info">プラン情報を読み込めませんでした</Alert>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
