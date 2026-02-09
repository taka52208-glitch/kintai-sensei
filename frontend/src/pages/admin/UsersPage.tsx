import { useState } from 'react';
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
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { usersApi, storesApi } from '../../services/api';
import type { User, UserRole, Store } from '../../types';

const ROLE_LABELS: Record<UserRole, string> = {
  admin: '管理者',
  store_manager: '店舗管理者',
  viewer: '閲覧者',
};

const ROLE_COLORS: Record<UserRole, 'error' | 'primary' | 'default'> = {
  admin: 'error',
  store_manager: 'primary',
  viewer: 'default',
};

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [form, setForm] = useState({
    email: '',
    role: 'store_manager' as UserRole,
    storeId: '',
  });
  const [error, setError] = useState('');
  const [inviteResult, setInviteResult] = useState<{ email: string; password: string } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);

  // ユーザー一覧取得
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list(),
  });

  // 店舗一覧取得
  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storesApi.list(),
  });

  // 招待
  const inviteMutation = useMutation({
    mutationFn: () => usersApi.invite(form),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleCloseDialog();
      setInviteResult({
        email: data.user.email,
        password: data.temporary_password,
      });
    },
    onError: () => {
      setError('招待に失敗しました');
    },
  });

  // 更新
  const updateMutation = useMutation({
    mutationFn: () => usersApi.update(editUser!.id, {
      role: form.role,
      storeId: form.storeId || undefined,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleCloseDialog();
    },
    onError: () => {
      setError('更新に失敗しました');
    },
  });

  // 削除
  const deleteMutation = useMutation({
    mutationFn: (id: string) => usersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditUser(user);
      setForm({
        email: user.email,
        role: user.role,
        storeId: user.storeId || '',
      });
    } else {
      setEditUser(null);
      setForm({
        email: '',
        role: 'store_manager',
        storeId: '',
      });
    }
    setError('');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditUser(null);
    setError('');
  };

  const handleSubmit = () => {
    if (editUser) {
      updateMutation.mutate();
    } else {
      inviteMutation.mutate();
    }
  };

  const users: User[] = usersData?.items || [];
  const stores: Store[] = storesData?.items || [];

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              ユーザー管理
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              ユーザーを招待
            </Button>
          </Box>

          {isLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>名前</TableCell>
                    <TableCell>メールアドレス</TableCell>
                    <TableCell>ロール</TableCell>
                    <TableCell>所属店舗</TableCell>
                    <TableCell>状態</TableCell>
                    <TableCell align="center">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Chip
                          label={ROLE_LABELS[user.role]}
                          size="small"
                          color={ROLE_COLORS[user.role]}
                        />
                      </TableCell>
                      <TableCell>{user.storeName || '---'}</TableCell>
                      <TableCell>
                        <Chip
                          label={user.isActive ? '有効' : '無効'}
                          size="small"
                          color={user.isActive ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="編集">
                          <IconButton size="small" onClick={() => handleOpenDialog(user)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="削除">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setDeleteTarget(user)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* 招待完了ダイアログ */}
      <Dialog open={!!inviteResult} onClose={() => setInviteResult(null)} maxWidth="sm" fullWidth>
        <DialogTitle>招待が完了しました</DialogTitle>
        <DialogContent>
          <Alert severity="success" sx={{ mb: 2 }}>
            以下の仮パスワードをユーザーにお伝えください。この画面を閉じると再表示できません。
          </Alert>
          <TextField
            fullWidth
            label="メールアドレス"
            value={inviteResult?.email || ''}
            margin="normal"
            InputProps={{ readOnly: true }}
          />
          <TextField
            fullWidth
            label="仮パスワード"
            value={inviteResult?.password || ''}
            margin="normal"
            InputProps={{ readOnly: true }}
            helperText="初回ログイン後、パスワードの変更を推奨してください"
          />
        </DialogContent>
        <DialogActions>
          <Button
            variant="outlined"
            onClick={() => {
              if (inviteResult) {
                navigator.clipboard.writeText(
                  `メールアドレス: ${inviteResult.email}\n仮パスワード: ${inviteResult.password}`
                );
              }
            }}
          >
            コピー
          </Button>
          <Button variant="contained" onClick={() => setInviteResult(null)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>

      {/* 削除確認ダイアログ */}
      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} maxWidth="xs" fullWidth>
        <DialogTitle>ユーザー削除の確認</DialogTitle>
        <DialogContent>
          <Typography>
            {deleteTarget?.name}（{deleteTarget?.email}）を削除しますか？
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteTarget(null)}>キャンセル</Button>
          <Button
            variant="contained"
            color="error"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (deleteTarget) {
                deleteMutation.mutate(deleteTarget.id, {
                  onSettled: () => setDeleteTarget(null),
                });
              }
            }}
          >
            削除
          </Button>
        </DialogActions>
      </Dialog>

      {/* 招待/編集ダイアログ */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editUser ? 'ユーザー編集' : 'ユーザー招待'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            fullWidth
            label="メールアドレス"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            margin="normal"
            disabled={!!editUser}
            required
          />
          <TextField
            select
            fullWidth
            label="ロール"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value as UserRole })}
            margin="normal"
          >
            {Object.entries(ROLE_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>{label}</MenuItem>
            ))}
          </TextField>
          <TextField
            select
            fullWidth
            label="所属店舗"
            value={form.storeId}
            onChange={(e) => setForm({ ...form, storeId: e.target.value })}
            margin="normal"
            helperText="管理者の場合は選択不要"
          >
            <MenuItem value="">なし（全店舗）</MenuItem>
            {stores.map((store) => (
              <MenuItem key={store.id} value={store.id}>{store.name}</MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={inviteMutation.isPending || updateMutation.isPending}
          >
            {editUser ? '更新' : '招待'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
