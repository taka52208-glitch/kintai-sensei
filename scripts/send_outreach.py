"""
営業メール一括送信スクリプト
送信先のtypeに応じて文面を自動切替

使い方:
    python scripts/send_outreach.py recipients.csv          # ドライラン（確認のみ）
    python scripts/send_outreach.py recipients.csv --send   # 実際に送信

CSVフォーマット:
    name,email,company,type
    川崎潤一,kawasaki@leaf-sr.jp,リーフレイバー,sharoushi
    ご担当者,info@shokudanren.jp,食団連,association
    オーナー,info@example-izakaya.com,居酒屋○○,restaurant

type: sharoushi / sharoushi_pivot / association / media / monitor / restaurant / followup
"""
import csv
import smtplib
import time
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# --- 設定 ---
GMAIL_ADDRESS = "taka52208@gmail.com"
GMAIL_APP_PASSWORD = "yivy ksza liok cxzr"
FROM_NAME = "勤怠先生"
SENDER_NAME = "勤怠先生 開発チーム"
REPLY_TO = GMAIL_ADDRESS

# Gmail制限
DAILY_LIMIT = 500
DELAY_SECONDS = 2  # 送信間隔（秒）

# --- 件名 ---
SUBJECTS = {
    "sharoushi": "【ご連携のご相談】飲食店向け勤怠チェックツール「勤怠先生」のご紹介",
    "sharoushi_pivot": "【新機能のご案内】社労士向け「予防労務」ツールとしてリニューアルしました - 勤怠先生",
    "association": "【ご紹介】飲食業界向け勤怠チェックシステム「勤怠先生」について",
    "media": "【掲載・連携のご相談】飲食業界特化の勤怠チェックシステム「勤怠先生」",
    "monitor": "【ご協力のお願い】飲食店向け勤怠チェックツール「勤怠先生」無料モニター募集",
    "restaurant": "{company}様 - 勤怠データの労務リスク、無料で診断しませんか？",
    "followup": "Re: 勤怠チェックシステム「勤怠先生」のご紹介（再送）",
}

# --- 共通フッター（特定電子メール法準拠） ---
FOOTER = """\
<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
<p style="color: #999; font-size: 11px;">
  勤怠先生 - 飲食業界特化の勤怠チェックシステム<br>
  https://kintai-sensei.vercel.app<br>
  <br>
  【送信者情報】<br>
  勤怠先生 開発チーム（個人開発）<br>
  連絡先: {reply_to}<br>
  <br>
  ※このメールは、貴社Webサイトで公開されている連絡先宛にお送りしています。<br>
  ※今後のメール配信を希望されない場合は {reply_to} まで「配信停止」とご返信ください。<br>
  ※このメールに心当たりがない場合は、お手数ですがそのまま破棄してください。
</p>
</div>
"""

# --- 社労士向けテンプレート ---
TEMPLATE_SHAROUSHI = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴事務所が飲食業の労務管理に精通されていることを拝見し、<strong>顧問先様へのご紹介</strong>という形での連携をご相談したく、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">連携メリット</h3>

<ul>
  <li>顧問先の労務リスクを事前に可視化し、是正勧告を未然に防止</li>
  <li>是正理由文の下書きをAI生成 → 先生方の業務効率化</li>
  <li>顧問先への付加価値提案として差別化に</li>
</ul>

<p><strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。導入に手間はかかりません。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<table style="border-collapse: collapse; width: 100%; margin-bottom: 16px;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;" colspan="2"><strong>デモアカウント（すぐにお試しいただけます）</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">URL</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><a href="https://kintai-sensei.vercel.app" style="color: #1976d2;">https://kintai-sensei.vercel.app</a></td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;">メール</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>store@example.com</code></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">パスワード</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>KintaiDev2026!</code></td>
  </tr>
</table>

<p>ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- 業界団体向けテンプレート ---
TEMPLATE_ASSOCIATION = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴団体が飲食業界の発展に取り組まれていることを拝見し、<strong>会員様への情報提供</strong>という形でお力添えできないかと思い、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<p>飲食業界は労基署の重点調査対象業種であり、中小飲食店にとって法令遵守は大きな課題です。<strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<table style="border-collapse: collapse; width: 100%; margin-bottom: 16px;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;" colspan="2"><strong>デモアカウント（すぐにお試しいただけます）</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">URL</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><a href="https://kintai-sensei.vercel.app" style="color: #1976d2;">https://kintai-sensei.vercel.app</a></td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;">メール</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>store@example.com</code></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">パスワード</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>KintaiDev2026!</code></td>
  </tr>
</table>

<p>会員様への情報提供の一環としてご紹介いただけましたら幸いです。ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- メディア向けテンプレート ---
TEMPLATE_MEDIA = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴メディアが飲食店経営者向けの情報発信をされていることを拝見し、<strong>記事掲載・サービス紹介</strong>のご相談をしたく、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong>（市場唯一の機能）</li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">ご提案</h3>

<ul>
  <li>サービス紹介記事の掲載（取材対応可）</li>
  <li>飲食店の勤怠管理に関する寄稿・監修</li>
  <li>読者向けの無料利用枠のご提供</li>
</ul>

<p><strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<table style="border-collapse: collapse; width: 100%; margin-bottom: 16px;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;" colspan="2"><strong>デモアカウント（すぐにお試しいただけます）</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">URL</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><a href="https://kintai-sensei.vercel.app" style="color: #1976d2;">https://kintai-sensei.vercel.app</a></td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;">メール</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>store@example.com</code></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">パスワード</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><code>KintaiDev2026!</code></td>
  </tr>
</table>

<p>ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- モニター募集テンプレート（飲食店オーナー向け） ---
TEMPLATE_MONITOR = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食店向けの勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>正式リリースに先立ち、<strong>3ヶ月間無料のモニター</strong>にご協力いただける飲食店様を探しております。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">無料モニター特典</h3>

<table style="border-collapse: collapse; width: 100%;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>利用料</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>3ヶ月間 完全無料</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>全機能利用</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">異常検知・是正理由文生成・レポート出力</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>終了後</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">フリープラン（10名以下無料）へ自動移行</td>
  </tr>
</table>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料でサインアップ
  </a>
</p>

<p>ご興味をお持ちいただけましたら <strong>{reply_to}</strong> までご連絡ください。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- 飲食企業向けテンプレート（エンドユーザー直接アプローチ） ---
TEMPLATE_RESTAURANT = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8; color: #333;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。{sender_name}と申します。</p>

<p>飲食業界で勤怠管理のお手伝いをしており、{company}様のことを拝見してご連絡いたしました。</p>

<p style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 16px; margin: 16px 0;">
  <strong>ご存知でしょうか？</strong><br>
  飲食業は労基署の重点調査対象業種で、<strong>是正勧告を受けた場合の対応コストは数十万円以上</strong>になることもあります。<br>
  しかし、普段の勤怠データに潜むリスクは、忙しい現場ではなかなか気づけません。
</p>

<p><strong>御社の勤怠CSVを1回アップロードするだけ</strong>で、以下を自動チェックします。</p>

<ul style="padding-left: 20px;">
  <li>残業時間の上限超過リスク</li>
  <li>休憩未取得・打刻漏れ</li>
  <li>深夜労働・連勤の法令違反の可能性</li>
</ul>

<p><strong>10名以下の店舗は永久無料</strong>、それ以上でも月額980円からです。</p>

<p>もしご興味があれば、<strong>このメールに「詳しく」とだけご返信ください</strong>。詳細をお送りいたします。</p>

<p>お忙しいところ恐れ入ります。</p>

<p>{sender_name}</p>
"""

# --- フォローアップテンプレート（全type共通） ---
TEMPLATE_FOLLOWUP = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>先日、飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」についてご連絡いたしました、{sender_name}です。</p>

<p>お忙しいところ恐れ入りますが、ご確認いただけましたでしょうか。</p>

<p>改めて要点のみお伝えいたします。</p>

<ul>
  <li>既存の勤怠CSVを取り込むだけで<strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応の<strong>是正理由文をAIが自動生成</strong>（市場唯一の機能）</li>
  <li><strong>10名以下は永久無料</strong>、初期費用0円</li>
</ul>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<p>ご興味がなければご返信不要です。少しでも気になる点がございましたら、お気軽に <strong>{reply_to}</strong> までご連絡ください。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- 社労士ピボット再アプローチテンプレート ---
TEMPLATE_SHAROUSHI_PIVOT = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>以前ご連絡いたしました、「勤怠先生」の{sender_name}です。</p>

<p>前回は飲食店向けツールとしてご紹介いたしましたが、その後<strong>社労士の先生方のワークフローに特化した「予防労務ツール」</strong>として大幅にリニューアルいたしました。改めてご案内させてください。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">何が変わったか</h3>

<p>先生方が日常的に行っている<strong>「顧問先の勤怠データを確認し、問題があれば是正対応する」</strong>という業務を、そのまま効率化する設計に変更しました。</p>

<table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
  <tr style="background: #e3f2fd;">
    <td style="border: 1px solid #ddd; padding: 8px; width: 40%;"><strong>以前（飲食店向け）</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>今回（社労士向け）</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">飲食店オーナーが自分で使う</td>
    <td style="border: 1px solid #ddd; padding: 8px;">先生方が顧問先の勤怠を一括チェック</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;">異常検知のみ</td>
    <td style="border: 1px solid #ddd; padding: 8px;">異常検知＋<strong>是正理由文の自動生成</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;">独自形式のCSV</td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>ジョブカン・KING OF TIME・Airシフト</strong>のCSVをそのまま取り込み</td>
  </tr>
</table>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">先生方のメリット</h3>

<ul>
  <li><strong>是正勧告の予防</strong>：顧問先の勤怠リスクを毎月チェック→問題を事前に潰せる</li>
  <li><strong>是正理由文の工数削減</strong>：Wordでの文書作成が不要に。AIが法令に沿った理由文を生成</li>
  <li><strong>顧問先への付加価値</strong>：「予防労務レポート」の定期提供で差別化</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">料金（社労士事務所向け）</h3>

<table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>お試し</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>無料</strong>（顧問先3社まで）</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>ライト</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">月額4,980円（顧問先10社まで）</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>スタンダード</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">月額9,800円（顧問先無制限）</td>
  </tr>
</table>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる（顧問先3社まで）
  </a>
</p>

<p>お忙しいところ恐れ入ります。もしご興味がございましたら、<strong>このメールにご返信いただくだけ</strong>で結構です。デモのご案内をいたします。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

TEMPLATES = {
    "sharoushi": TEMPLATE_SHAROUSHI,
    "sharoushi_pivot": TEMPLATE_SHAROUSHI_PIVOT,
    "association": TEMPLATE_ASSOCIATION,
    "media": TEMPLATE_MEDIA,
    "monitor": TEMPLATE_MONITOR,
    "restaurant": TEMPLATE_RESTAURANT,
    "followup": TEMPLATE_FOLLOWUP,
}


def load_recipients(csv_path: str) -> list[dict]:
    """CSVから送信先リストを読み込み"""
    recipients = []
    path = Path(csv_path)
    if not path.exists():
        print(f"エラー: {csv_path} が見つかりません")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email"):
                rtype = row.get("type", "monitor").strip()
                if rtype not in TEMPLATES:
                    print(f"警告: 不明なtype '{rtype}' → monitorとして処理")
                    rtype = "monitor"
                recipients.append({
                    "name": row.get("name", "ご担当者"),
                    "email": row["email"].strip(),
                    "company": row.get("company", ""),
                    "type": rtype,
                })
    return recipients


def send_outreach(recipients: list[dict], dry_run: bool = True) -> None:
    """営業メールを一括送信"""
    total = len(recipients)
    if total > DAILY_LIMIT:
        print(f"警告: 送信先が{total}件あります（日次上限: {DAILY_LIMIT}件）")
        print(f"最初の{DAILY_LIMIT}件のみ送信します。")
        recipients = recipients[:DAILY_LIMIT]
        total = DAILY_LIMIT

    print(f"\n{'='*60}")
    print(f"営業メール {'ドライラン' if dry_run else '送信'}")
    print(f"送信件数: {total}")
    print(f"送信元: {FROM_NAME} <{GMAIL_ADDRESS}>")
    print(f"{'='*60}\n")

    log_file = Path(f"scripts/send_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    smtp = None
    if not dry_run:
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        print("Gmail SMTP接続成功\n")

    with open(log_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "email", "company", "type", "status", "detail"])

        for i, r in enumerate(recipients, 1):
            template = TEMPLATES[r["type"]]
            subject = SUBJECTS[r["type"]]
            # 件名の{company}をパーソナライズ
            if "{company}" in subject:
                subject = subject.replace("{company}", r.get("company", ""))
            html = template.format(
                recipient_name=r["name"],
                sender_name=SENDER_NAME,
                reply_to=REPLY_TO,
                company=r.get("company", ""),
            ) + FOOTER.format(reply_to=REPLY_TO)

            type_label = {"sharoushi": "社労士", "sharoushi_pivot": "社労士再", "association": "団体", "media": "メディア", "monitor": "モニター", "restaurant": "飲食企業"}
            print(f"[{i}/{total}] [{type_label.get(r['type'], r['type'])}] {r['name']} <{r['email']}>", end=" ")

            if dry_run:
                print("(ドライラン)")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "dry_run", "",
                ])
                continue

            try:
                msg = MIMEMultipart("alternative")
                msg["From"] = f"{FROM_NAME} <{GMAIL_ADDRESS}>"
                msg["To"] = r["email"]
                msg["Subject"] = subject
                msg["Reply-To"] = REPLY_TO
                msg.attach(MIMEText(html, "html", "utf-8"))
                smtp.sendmail(GMAIL_ADDRESS, r["email"], msg.as_string())
                print("送信成功")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "sent", "ok",
                ])
            except Exception as e:
                print(f"送信失敗: {e}")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "failed", str(e),
                ])

            if i < total:
                time.sleep(DELAY_SECONDS)

    if smtp:
        smtp.quit()

    print(f"\n送信ログ: {log_file}")


def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python scripts/send_outreach.py recipients.csv          # ドライラン")
        print("  python scripts/send_outreach.py recipients.csv --send   # 実際に送信")
        print("")
        print("CSVフォーマット:")
        print("  name,email,company,type")
        print("  川崎潤一,kawasaki@leaf-sr.jp,リーフレイバー,sharoushi")
        print("")
        print("type: sharoushi / sharoushi_pivot / association / media / monitor / restaurant / followup")
        sys.exit(0)

    csv_path = sys.argv[1]
    dry_run = "--send" not in sys.argv

    recipients = load_recipients(csv_path)
    if not recipients:
        print("エラー: 送信先が0件です。")
        sys.exit(1)

    print(f"送信先: {len(recipients)}件読み込み")

    if not dry_run:
        confirm = input("本当に送信しますか？ (yes/no): ")
        if confirm.lower() != "yes":
            print("キャンセルしました。")
            sys.exit(0)

    send_outreach(recipients, dry_run=dry_run)


if __name__ == "__main__":
    main()
