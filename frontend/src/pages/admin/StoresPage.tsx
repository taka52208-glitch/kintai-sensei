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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { storesApi } from '../../services/api';
import type { Store } from '../../types';

export default function StoresPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editStore, setEditStore] = useState<Store | null>(null);
  const [form, setForm] = useState({
    code: '',
    name: '',
  });
  const [error, setError] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<Store | null>(null);

  // 店舗一覧取得
  const { data: storesData, isLoading } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storesApi.list(),
  });

  // 作成
  const createMutation = useMutation({
    mutationFn: () => storesApi.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
      handleCloseDialog();
    },
    onError: () => {
      setError('作成に失敗しました');
    },
  });

  // 更新
  const updateMutation = useMutation({
    mutationFn: () => storesApi.update(editStore!.id, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
      handleCloseDialog();
    },
    onError: () => {
      setError('更新に失敗しました');
    },
  });

  // 削除
  const deleteMutation = useMutation({
    mutationFn: (id: string) => storesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
    },
  });

  const handleOpenDialog = (store?: Store) => {
    if (store) {
      setEditStore(store);
      setForm({
        code: store.code,
        name: store.name,
      });
    } else {
      setEditStore(null);
      setForm({
        code: '',
        name: '',
      });
    }
    setError('');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditStore(null);
    setError('');
  };

  const handleSubmit = () => {
    if (editStore) {
      updateMutation.mutate();
    } else {
      createMutation.mutate();
    }
  };

  const stores: Store[] = storesData?.items || [];

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              店舗管理
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              店舗を追加
            </Button>
          </Box>

          {isLoading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : stores.length === 0 ? (
            <Box textAlign="center" p={4}>
              <Typography color="text.secondary">
                店舗がありません
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>店舗コード</TableCell>
                    <TableCell>店舗名</TableCell>
                    <TableCell>作成日</TableCell>
                    <TableCell align="center">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stores.map((store) => (
                    <TableRow key={store.id} hover>
                      <TableCell>{store.code}</TableCell>
                      <TableCell>{store.name}</TableCell>
                      <TableCell>
                        {new Date(store.createdAt).toLocaleDateString('ja-JP')}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="編集">
                          <IconButton size="small" onClick={() => handleOpenDialog(store)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="削除">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setDeleteTarget(store)}
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

      {/* 削除確認ダイアログ */}
      <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} maxWidth="xs" fullWidth>
        <DialogTitle>店舗削除の確認</DialogTitle>
        <DialogContent>
          <Typography>
            {deleteTarget?.name}（{deleteTarget?.code}）を削除しますか？関連するデータも削除されます。
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

      {/* 作成/編集ダイアログ */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editStore ? '店舗編集' : '店舗追加'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            fullWidth
            label="店舗コード"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            margin="normal"
            required
            helperText="例: STORE001"
          />
          <TextField
            fullWidth
            label="店舗名"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            margin="normal"
            required
            helperText="例: 渋谷店"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={createMutation.isPending || updateMutation.isPending || !form.code || !form.name}
          >
            {editStore ? '更新' : '追加'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
