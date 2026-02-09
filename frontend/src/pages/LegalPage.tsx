import { useEffect, useState } from 'react';
import { Box, Card, CardContent, CircularProgress, Typography, Button } from '@mui/material';
import { ArrowBack as BackIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const LEGAL_DOCS: Record<string, { title: string; file: string }> = {
  terms: { title: '利用規約', file: '/legal/terms-of-service.md' },
  privacy: { title: 'プライバシーポリシー', file: '/legal/privacy-policy.md' },
  tokushoho: { title: '特定商取引法に基づく表記', file: '/legal/tokushoho.md' },
};

/** HTMLエンティティをエスケープ */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** 簡易マークダウン → HTML変換（エスケープ済みテキストのみ処理） */
function renderMarkdown(md: string): string {
  return escapeHtml(md)
    // テーブル
    .replace(/^\|(.+)\|$/gm, (match) => {
      const cells = match.split('|').filter(Boolean).map((c) => c.trim());
      if (cells.every((c) => /^[-:]+$/.test(c))) return '';
      const tag = match.includes('---') ? 'td' : 'td';
      return `<tr>${cells.map((c) => `<${tag}>${c}</${tag}>`).join('')}</tr>`;
    })
    // ヘッダー
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // 太字
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 水平線
    .replace(/^---$/gm, '<hr/>')
    // リスト
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    // 引用（エスケープ後の &gt; にマッチ）
    .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
    // 段落
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
}

export default function LegalPage({ docKey }: { docKey: string }) {
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const doc = LEGAL_DOCS[docKey];

  useEffect(() => {
    fetch(doc.file)
      .then((res) => {
        if (!res.ok) throw new Error('Not found');
        return res.text();
      })
      .then((text) => {
        setContent(text);
        setLoading(false);
      })
      .catch(() => {
        setContent('ドキュメントの読み込みに失敗しました。');
        setLoading(false);
      });
  }, [doc.file]);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4, px: 2 }}>
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate(-1)}
          sx={{ mb: 2 }}
        >
          戻る
        </Button>
        <Card>
          <CardContent sx={{ p: { xs: 3, md: 5 } }}>
            <Typography variant="h5" fontWeight={700} gutterBottom>
              {doc.title}
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Box
                sx={{
                  '& h2': { fontSize: '1.3rem', fontWeight: 700, mt: 4, mb: 1 },
                  '& h3': { fontSize: '1.1rem', fontWeight: 700, mt: 3, mb: 1 },
                  '& h4': { fontSize: '1rem', fontWeight: 600, mt: 2, mb: 0.5 },
                  '& p': { fontSize: '0.9rem', lineHeight: 1.8, mb: 1 },
                  '& li': { fontSize: '0.9rem', lineHeight: 1.8, ml: 2 },
                  '& hr': { my: 3, border: 'none', borderTop: '1px solid', borderColor: 'divider' },
                  '& table': { width: '100%', borderCollapse: 'collapse', my: 2, fontSize: '0.85rem' },
                  '& td': { border: '1px solid #ddd', p: 1 },
                  '& blockquote': { borderLeft: '3px solid', borderColor: 'primary.main', pl: 2, ml: 0, my: 2, color: 'text.secondary', fontStyle: 'italic' },
                  '& strong': { fontWeight: 700 },
                }}
                dangerouslySetInnerHTML={{ __html: `<p>${renderMarkdown(content)}</p>` }}
              />
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
