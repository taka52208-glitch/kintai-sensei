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
    title: '顧問先の勤怠異常を自動検知',
    description:
      '打刻漏れ、休憩不足、長時間労働、深夜勤務など8つのルールで、顧問先企業の勤怠CSVを自動チェック。ジョブカン・KING OF TIME・Airシフトに対応。',
  },
  {
    icon: <AutoFixHighIcon sx={{ fontSize: 48 }} />,
    title: 'AIが是正理由文を自動生成',
    description:
      '検知した異常に対し、原因・対応・再発防止を組み合わせた是正理由文をAIが生成。Wordでの文書作成工数を大幅に削減できます。',
  },
  {
    icon: <AssessmentIcon sx={{ fontSize: 48 }} />,
    title: '顧問先別レポートを一括出力',
    description:
      '顧問先企業ごとの月次レポートをCSV/PDFで出力。個人情報マスク機能付きで、臨検対策の証跡としても活用できます。',
  },
];

const steps = [
  {
    icon: <UploadFileIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 1',
    title: '顧問先のCSVを取り込み',
    description: 'ジョブカン・KING OF TIME・Airシフト・汎用CSVに対応。顧問先ごとにデータを管理。',
  },
  {
    icon: <FindInPageIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 2',
    title: '異常を自動検知',
    description: '8種類のルールで瞬時にチェック。重要度・種別ごとに一覧表示。複数企業を横断管理。',
  },
  {
    icon: <DescriptionIcon sx={{ fontSize: 40 }} />,
    step: 'STEP 3',
    title: '是正理由文を生成',
    description: '原因と対応を選ぶだけ。Wordでの文書作成が不要に。顧問先への報告書もワンクリック。',
  },
];

const plans = [
  {
    name: 'お試し',
    price: '0',
    unit: '円',
    period: '',
    target: '顧問先3社まで',
    features: [
      '全8ルールで異常検知',
      '是正理由文 月3件まで',
      'CSVレポート出力',
      'メールサポート',
      'データ保持 12ヶ月',
    ],
    cta: '無料で始める',
    highlight: false,
  },
  {
    name: 'ライト',
    price: '4,980',
    unit: '円/月',
    period: '（税込）',
    target: '顧問先10社までの個人事務所',
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
    name: 'スタンダード',
    price: '9,800',
    unit: '円/月',
    period: '（税込）',
    target: '顧問先無制限の社労士法人',
    features: [
      '全ルール + カスタムルール',
      '是正理由文 無制限 + テンプレカスタム',
      'CSV + PDF + API出力',
      '業種別検知プリセット',
      '複数スタッフID対応',
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
    description: 'JWT認証、権限制御、ブルートフォース対策、個人情報マスク機能を標準装備。顧問先の従業員データを安全に管理。',
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 36, color: 'primary.main' }} />,
    title: '既存の勤怠SaaSと連携',
    description: 'ジョブカン・KING OF TIME・AirシフトのCSVをそのまま取り込み。既存システムを変更する必要はありません。',
  },
  {
    icon: <SupportAgentIcon sx={{ fontSize: 36, color: 'primary.main' }} />,
    title: '是正対応の工数を1/3に',
    description: 'Wordでの文書作成が不要に。是正理由文の生成からレポート出力まで、すべてクラウドで完結。',
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
            顧問先の勤怠異常、
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
            顧問先のジョブカン・KING OF TIMEデータを取り込むだけで、勤怠異常を自動検知。
            <br />
            さらに、是正理由文までAIが自動生成。Wordでの文書作成はもう不要です。
          </Typography>
          <Typography
            variant="body2"
            sx={{ mb: 4, opacity: 0.85, fontWeight: 600 }}
          >
            社労士のための予防労務ツール。是正勧告を受ける前に、異常を検知し対応を完結。
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
            初期費用0円 / クレジットカード不要 / 顧問先3社までずっと無料
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
          社労士の業務を変える3つの特長
        </Typography>
        <Typography
          variant="body2"
          textAlign="center"
          color="text.secondary"
          sx={{ mb: 6 }}
        >
          顧問先の勤怠チェックから是正理由文の作成まで、ワンストップで完結
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
            顧問先の勤怠SaaSからCSVを取り込むだけ。最短30秒で異常検知が完了
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
            顧問先3社まで無料。まずはお試しプランで始めてみませんか
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
            ※ 顧問先企業数は、勤怠データが1件以上登録されている企業数に基づき算定
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
            顧問先の勤怠データ、まず1社チェックしてみませんか？
          </Typography>
          <Typography variant="body2" sx={{ mb: 3, opacity: 0.9 }}>
            顧問先3社まで無料。初期費用0円・クレジットカード不要で今すぐ始められます。
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
                社労士のための予防労務ツール
                <br />
                勤怠異常検知＋AI是正理由文生成
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
