import { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { healthApi } from '../services/api';
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
  Stack,
} from '@mui/material';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../services/api';
import { config } from '../config';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  // バックエンドのウォームアップ（Renderコールドスタート対策）
  useEffect(() => {
    healthApi.ping();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.login(email, password);
      // バックエンドのsnake_caseをフロントエンドのcamelCaseに変換
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
      setAuth(user, response.access_token, response.refresh_token);
      navigate('/dashboard');
    } catch (err: unknown) {
      const error = err as { response?: { status?: number; data?: unknown }; message?: string };
      if (error.response?.status === 401) {
        setError('メールアドレスまたはパスワードが正しくありません');
      } else if (error.response?.status === 429) {
        setError('ログイン試行回数が上限に達しました。しばらく待ってからお試しください');
      } else {
        setError(`ログインエラー: ${error.message || JSON.stringify(error.response?.data) || '不明なエラー'}`);
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
      <Card sx={{ maxWidth: 400, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom textAlign="center">
            {config.appName}
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" mb={4}>
            勤怠異常検知・是正理由作成システム
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="メールアドレス"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              autoComplete="email"
              autoFocus
            />
            <TextField
              fullWidth
              label="パスワード"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              autoComplete="current-password"
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? <CircularProgress size={24} /> : 'ログイン'}
            </Button>
          </Box>

          <Stack direction="row" justifyContent="center" sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              アカウントをお持ちでない方は{' '}
              <Link component={RouterLink} to="/signup">
                新規登録
              </Link>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
