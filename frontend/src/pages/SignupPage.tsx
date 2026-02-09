import { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { healthApi, authApi } from '../services/api';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link,
  Checkbox,
  FormControlLabel,
  Stack,
} from '@mui/material';
import { useAuthStore } from '../stores/authStore';
import { trackEvent } from '../utils/analytics';

export default function SignupPage() {
  const [organizationName, setOrganizationName] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  useEffect(() => {
    healthApi.ping();
  }, []);

  const passwordErrors = (() => {
    if (!password) return [];
    const errors: string[] = [];
    if (password.length < 8) errors.push('8文字以上');
    if (!/[A-Z]/.test(password)) errors.push('大文字を含む');
    if (!/[0-9]/.test(password)) errors.push('数字を含む');
    return errors;
  })();

  const isFormValid =
    organizationName.trim() &&
    name.trim() &&
    email.trim() &&
    password.length >= 8 &&
    passwordErrors.length === 0 &&
    agreeTerms;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.signup({
        organization_name: organizationName,
        name,
        email,
        password,
      });

      const user = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        role: response.user.role as 'admin' | 'store_manager' | 'viewer',
        storeId: response.user.store_id,
        storeName: response.user.store_name,
        isActive: true,
        createdAt: new Date().toISOString(),
      };

      setAuth(user, response.access_token);
      trackEvent('sign_up', { method: 'email' });
      navigate('/dashboard');
    } catch (err: unknown) {
      const error = err as { response?: { status?: number; data?: { detail?: string } }; message?: string };
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('登録に失敗しました。もう一度お試しください。');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" component="h1" gutterBottom textAlign="center" fontWeight={700}>
            勤怠先生に登録
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" mb={3}>
            無料ではじめる。10名以下はずっと無料。
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="組織名（会社名・店舗名）"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              margin="normal"
              required
              placeholder="例: 株式会社○○ / ○○食堂"
              autoFocus
            />
            <TextField
              fullWidth
              label="お名前"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
              required
              autoComplete="name"
            />
            <TextField
              fullWidth
              label="メールアドレス"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              autoComplete="email"
            />
            <TextField
              fullWidth
              label="パスワード"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              autoComplete="new-password"
              helperText={
                password && passwordErrors.length > 0
                  ? `必要: ${passwordErrors.join('、')}`
                  : password
                    ? '条件を満たしています'
                    : '8文字以上、大文字・数字を含む'
              }
              error={password.length > 0 && passwordErrors.length > 0}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                  size="small"
                />
              }
              label={
                <Typography variant="body2">
                  <Link href="/terms" target="_blank" rel="noopener">利用規約</Link>
                  {' および '}
                  <Link href="/privacy" target="_blank" rel="noopener">プライバシーポリシー</Link>
                  に同意します
                </Typography>
              }
              sx={{ mt: 1 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading || !isFormValid}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : '無料で登録'}
            </Button>
          </Box>

          <Stack direction="row" justifyContent="center" sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              アカウントをお持ちの方は{' '}
              <Link component={RouterLink} to="/login">
                ログイン
              </Link>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
