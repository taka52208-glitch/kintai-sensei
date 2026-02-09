import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { healthApi } from '../services/api';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Divider,
  Grid,
  Link,
  Stack,
  Typography,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import AssessmentIcon from '@mui/icons-material/Assessment';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';

const features = [
  {
    icon: <SearchIcon sx={{ fontSize: 48 }} />,
    title: '8種類の異常を自動検知',
    description:
      '打刻漏れ、休憩不足、長時間労働、深夜勤務、時刻不整合など、労基法に関わる8つのルールでCSVデータを自動チェック。',
  },
  {
    icon: <AutoFixHighIcon sx={{ fontSize: 48 }} />,
    title: 'AIが是正理由文を自動生成',
    description:
      '検知した異常に対し、原因・対応・再発防止を組み合わせた是正理由文をAIが生成。社内記録用・本人確認用・監査向けの3種類に対応。',
  },
  {
    icon: <AssessmentIcon sx={{ fontSize: 48 }} />,
    title: '監査対応レポートを即時出力',
    description:
      '月次レポートをCSV/PDFで出力。個人情報マスク機能付きで、労基署への提出資料もワンクリック。',
  },
];

const steps = [
  {
    icon: <UploadFileIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 1',
    title: 'CSVをアップロード',
    description: 'ジョブカン・Airシフト・汎用CSVに対応。ドラッグ&ドロップで取り込み完了。',
  },
  {
    icon: <FindInPageIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 2',
    title: '異常を自動検知',
    description: '8種類のルールで瞬時にチェック。重要度・種別ごとに一覧表示。',
  },
  {
    icon: <DescriptionIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 3',
    title: '是正理由文を生成',
    description: '原因と対応を選ぶだけ。AIが自然な日本語の是正理由文を生成します。',
  },
];

const plans = [
  {
    name: 'フリー',
    price: '0',
    unit: '円',
    period: '',
    target: '10名以下の小規模店舗',
    features: [
      '全8ルールで異常検知',
      '是正理由文 月5件まで',
      'CSVレポート出力',
      'メールサポート',
      'データ保持 12ヶ月',
    ],
    cta: '無料で始める',
    highlight: false,
  },
  {
    name: 'スタンダード',
    price: '300',
    unit: '円/人',
    period: '（税抜）',
    target: '50名以下のチェーン店',
    features: [
      '全8ルールで異常検知',
      '是正理由文 無制限',
      'CSV + PDFレポート',
      '検知ルールのカスタム',
      'メール + チャットサポート',
      'データ保持 24ヶ月',
    ],
    cta: '無料で試す',
    highlight: true,
  },
  {
    name: 'プロ',
    price: '500',
    unit: '円/人',
    period: '（税抜）',
    target: '大規模チェーン・FC本部',
    features: [
      '全ルール + カスタムルール',
      '是正理由文 無制限 + テンプレカスタム',
      'CSV + PDF + API出力',
      '業態別プリセット',
      '専任サポート担当',
      'データ保持 無制限',
    ],
    cta: 'お問い合わせ',
    highlight: false,
  },
];

const strengths = [
  {
    icon: <SecurityIcon sx={{ fontSize: 36, color: 'primary.main' }} />,
    title: 'セキュリティ',
    description: 'JWT認証、権限制御、ブルートフォース対策、個人情報マスク機能を標準装備。',
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 36, color: 'primary.main' }} />,
    title: '初期費用0円・即日利用開始',
    description: 'クレジットカード不要で無料プランをすぐに利用開始。有料プランも初期費用0円。',
  },
  {
    icon: <SupportAgentIcon sx={{ fontSize: 36, color: 'primary.main' }} />,
    title: '飲食業界に特化',
    description: 'シフト制・変形労働時間制・深夜勤務など、飲食店特有の勤怠パターンに対応した検知ルール。',
  },
];

export default function LandingPage() {
  const navigate = useNavigate();

  // バックエンドのウォームアップ（Renderコールドスタート対策）
  useEffect(() => {
    healthApi.ping();
  }, []);

  const handleCta = () => {
    navigate('/signup');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      {/* ヘッダー */}
      <AppBar position="sticky" color="inherit" elevation={1}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" fontWeight={700} color="primary">
            勤怠先生
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleLogin}
            >
              ログイン
            </Button>
            <Button
              variant="contained"
              size="small"
              onClick={handleCta}
            >
              無料で始める
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* ヒーローセクション */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          px: 2,
        }}
      >
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography
            variant="h1"
            component="h1"
            sx={{
              fontSize: { xs: '1.75rem', md: '2.5rem' },
              fontWeight: 700,
              mb: 2,
              lineHeight: 1.4,
            }}
          >
            飲食店の勤怠異常、
            <br />
            見逃していませんか？
          </Typography>
          <Typography
            variant="h6"
            sx={{
              mb: 1,
              fontSize: { xs: '0.95rem', md: '1.15rem' },
              opacity: 0.95,
              fontWeight: 400,
              lineHeight: 1.8,
            }}
          >
            CSVを取り込むだけで休憩不足・長時間労働・打刻漏れを自動検知。
            <br />
            さらに、労基署対応の是正理由文までAIが自動生成。
          </Typography>
          <Typography
            variant="body2"
            sx={{ mb: 4, opacity: 0.85, fontWeight: 600 }}
          >
            「検知して終わり」ではなく「対応まで完結」する、飲食業界唯一の勤怠チェックシステム。
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            justifyContent="center"
          >
            <Button
              variant="contained"
              size="large"
              onClick={handleCta}
              sx={{
                bgcolor: 'white',
                color: 'primary.dark',
                fontWeight: 700,
                px: 4,
                py: 1.5,
                fontSize: '1rem',
                '&:hover': { bgcolor: '#e3f2fd' },
              }}
            >
              無料で始める
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleCta}
              sx={{
                borderColor: 'white',
                color: 'white',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
              }}
            >
              デモを見る
            </Button>
          </Stack>
          <Typography variant="caption" sx={{ mt: 2, display: 'block', opacity: 0.8 }}>
            初期費用0円 / クレジットカード不要 / 10名以下ずっと無料
          </Typography>
        </Container>
      </Box>

      {/* 機能紹介 */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography
          variant="h2"
          component="h2"
          textAlign="center"
          sx={{ mb: 1, fontSize: { xs: '1.3rem', md: '1.5rem' } }}
        >
          勤怠先生の3つの特長
        </Typography>
        <Typography
          variant="body2"
          textAlign="center"
          color="text.secondary"
          sx={{ mb: 6 }}
        >
          異常の検知から是正理由文の作成まで、ワンストップで対応
        </Typography>
        <Grid container spacing={4}>
          {features.map((f) => (
            <Grid size={{ xs: 12, md: 4 }} key={f.title}>
              <Card
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  transition: 'box-shadow 0.2s',
                  '&:hover': { boxShadow: 4 },
                }}
                elevation={1}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>{f.icon}</Box>
                  <Typography variant="h6" fontWeight={600} sx={{ mb: 1.5 }}>
                    {f.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" lineHeight={1.8}>
                    {f.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* 使い方 3ステップ */}
      <Box sx={{ bgcolor: 'white', py: { xs: 6, md: 10 } }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            textAlign="center"
            sx={{ mb: 1, fontSize: { xs: '1.3rem', md: '1.5rem' } }}
          >
            かんたん3ステップ
          </Typography>
          <Typography
            variant="body2"
            textAlign="center"
            color="text.secondary"
            sx={{ mb: 6 }}
          >
            専門知識は不要。CSVをアップロードするだけで始められます
          </Typography>
          <Grid container spacing={4} alignItems="stretch">
            {steps.map((s) => (
              <Grid size={{ xs: 12, md: 4 }} key={s.step}>
                <Box
                  sx={{
                    textAlign: 'center',
                    p: 3,
                    height: '100%',
                  }}
                >
                  <Box sx={{ color: 'primary.main', mb: 1 }}>{s.icon}</Box>
                  <Typography
                    variant="caption"
                    fontWeight={700}
                    color="primary"
                    sx={{ letterSpacing: 1 }}
                  >
                    {s.step}
                  </Typography>
                  <Typography variant="h6" fontWeight={600} sx={{ mt: 1, mb: 1.5 }}>
                    {s.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" lineHeight={1.8}>
                    {s.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* 強み */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 8 } }}>
        <Grid container spacing={4}>
          {strengths.map((s) => (
            <Grid size={{ xs: 12, md: 4 }} key={s.title}>
              <Stack direction="row" spacing={2} alignItems="flex-start">
                {s.icon}
                <Box>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 0.5 }}>
                    {s.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" lineHeight={1.7}>
                    {s.description}
                  </Typography>
                </Box>
              </Stack>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* 料金プラン */}
      <Box sx={{ bgcolor: 'white', py: { xs: 6, md: 10 } }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            textAlign="center"
            sx={{ mb: 1, fontSize: { xs: '1.3rem', md: '1.5rem' } }}
          >
            料金プラン
          </Typography>
          <Typography
            variant="body2"
            textAlign="center"
            color="text.secondary"
            sx={{ mb: 6 }}
          >
            10名以下は無料。まずはフリープランでお試しください
          </Typography>
          <Grid container spacing={3} justifyContent="center">
            {plans.map((p) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={p.name}>
                <Card
                  elevation={p.highlight ? 4 : 1}
                  sx={{
                    height: '100%',
                    border: p.highlight ? '2px solid' : '1px solid',
                    borderColor: p.highlight ? 'primary.main' : 'divider',
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  {p.highlight && (
                    <Box
                      sx={{
                        bgcolor: 'primary.main',
                        color: 'white',
                        textAlign: 'center',
                        py: 0.5,
                        fontSize: '0.75rem',
                        fontWeight: 700,
                      }}
                    >
                      おすすめ
                    </Box>
                  )}
                  <CardContent sx={{ p: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="h6" fontWeight={700} textAlign="center">
                      {p.name}
                    </Typography>
                    <Box sx={{ textAlign: 'center', my: 2 }}>
                      <Typography
                        component="span"
                        sx={{ fontSize: '2.5rem', fontWeight: 700, color: 'primary.main' }}
                      >
                        {p.price}
                      </Typography>
                      <Typography component="span" variant="body2" color="text.secondary">
                        {p.unit}
                      </Typography>
                      {p.period && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          {p.period}
                        </Typography>
                      )}
                    </Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      textAlign="center"
                      sx={{ mb: 2 }}
                    >
                      {p.target}
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Stack spacing={1} sx={{ flex: 1 }}>
                      {p.features.map((feat) => (
                        <Stack direction="row" spacing={1} alignItems="center" key={feat}>
                          <CheckCircleOutlineIcon
                            sx={{ fontSize: 18, color: 'success.main' }}
                          />
                          <Typography variant="body2">{feat}</Typography>
                        </Stack>
                      ))}
                    </Stack>
                    <Button
                      variant={p.highlight ? 'contained' : 'outlined'}
                      fullWidth
                      sx={{ mt: 3 }}
                      onClick={handleCta}
                    >
                      {p.cta}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          <Typography
            variant="caption"
            display="block"
            textAlign="center"
            color="text.secondary"
            sx={{ mt: 3 }}
          >
            ※ アクティブ従業員数（当月に勤怠データが1件以上ある従業員数）に基づき算定
          </Typography>
        </Container>
      </Box>

      {/* CTA セクション */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1565c0 0%, #1976d2 100%)',
          color: 'white',
          py: { xs: 6, md: 8 },
          textAlign: 'center',
        }}
      >
        <Container maxWidth="sm">
          <Typography
            variant="h5"
            fontWeight={700}
            sx={{ mb: 2, fontSize: { xs: '1.2rem', md: '1.5rem' } }}
          >
            まずは無料で、勤怠データをチェックしてみませんか？
          </Typography>
          <Typography variant="body2" sx={{ mb: 3, opacity: 0.9 }}>
            10名以下なら、ずっと無料。初期費用0円・クレジットカード不要で今すぐ始められます。
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={handleCta}
            sx={{
              bgcolor: 'white',
              color: 'primary.dark',
              fontWeight: 700,
              px: 5,
              py: 1.5,
              fontSize: '1rem',
              '&:hover': { bgcolor: '#e3f2fd' },
            }}
          >
            無料で始める
          </Button>
        </Container>
      </Box>

      {/* 免責注記 */}
      <Box sx={{ bgcolor: '#f9f9f9', py: 3, px: 2 }}>
        <Container maxWidth="md">
          <Typography variant="caption" color="text.secondary" lineHeight={1.8}>
            ※ 本サービスは、労働基準法その他の労働関係法令の遵守を判定・保証するものではありません。
            異常検知の結果は「要確認」「アラート」「疑い」として情報提供するものであり、法令違反の有無を確定するものではありません。
            AI生成された是正理由文は参考情報です。労働基準監督署への提出等に利用する場合は、社会保険労務士等の専門家にご確認ください。
          </Typography>
        </Container>
      </Box>

      {/* フッター */}
      <Box
        component="footer"
        sx={{ bgcolor: '#263238', color: 'grey.400', py: 5, px: 2 }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <Typography variant="subtitle2" color="white" fontWeight={700} sx={{ mb: 2 }}>
                勤怠先生
              </Typography>
              <Typography variant="caption" lineHeight={1.8}>
                飲食業界特化の勤怠異常検知＋
                <br />
                AI是正理由文生成サービス
              </Typography>
            </Grid>
            <Grid size={{ xs: 6, sm: 4 }}>
              <Typography variant="subtitle2" color="white" fontWeight={700} sx={{ mb: 2 }}>
                サービス
              </Typography>
              <Stack spacing={1}>
                <Link href="#" color="inherit" underline="hover" variant="caption">
                  機能紹介
                </Link>
                <Link href="#" color="inherit" underline="hover" variant="caption">
                  料金プラン
                </Link>
                <Link href="/login" color="inherit" underline="hover" variant="caption">
                  ログイン
                </Link>
              </Stack>
            </Grid>
            <Grid size={{ xs: 6, sm: 4 }}>
              <Typography variant="subtitle2" color="white" fontWeight={700} sx={{ mb: 2 }}>
                法務情報
              </Typography>
              <Stack spacing={1}>
                <Link href="/terms" color="inherit" underline="hover" variant="caption">
                  利用規約
                </Link>
                <Link href="/privacy" color="inherit" underline="hover" variant="caption">
                  プライバシーポリシー
                </Link>
                <Link href="/tokushoho" color="inherit" underline="hover" variant="caption">
                  特定商取引法に基づく表記
                </Link>
              </Stack>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3, borderColor: 'grey.700' }} />
          <Typography variant="caption" textAlign="center" display="block">
            &copy; {new Date().getFullYear()} 勤怠先生 All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
