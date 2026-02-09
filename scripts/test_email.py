"""Resend テスト送信スクリプト

使い方:
    python scripts/test_email.py                       # デフォルト宛先
    python scripts/test_email.py someone@example.com   # 指定宛先
"""
import resend
import sys

# --- 設定 ---
RESEND_API_KEY = "re_4KHgS6FR_F9yQuTmXU5T5n8WunAs9gHiB"
FROM_ADDRESS = "onboarding@resend.dev"  # Resend無料テストドメイン（独自ドメイン不要）
FROM_NAME = "勤怠先生"
TEST_TO = "taka52208@gmail.com"

resend.api_key = RESEND_API_KEY


def send_test_email(to_address: str = TEST_TO) -> None:
    """テストメールを送信"""
    params: resend.Emails.SendParams = {
        "from": f"{FROM_NAME} <{FROM_ADDRESS}>",
        "to": [to_address],
        "subject": "【テスト】勤怠先生 メール送信テスト",
        "html": """
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1976d2;">勤怠先生 メール送信テスト</h2>
            <p>このメールは Resend API のテスト送信です。</p>
            <p>正常に受信できていれば、メール営業基盤のセットアップは完了です。</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
            <p style="color: #666; font-size: 12px;">
                勤怠先生 - 飲食業界特化の勤怠チェックシステム<br>
                https://kintai-sensei.vercel.app
            </p>
        </div>
        """,
    }
    email = resend.Emails.send(params)
    print(f"送信成功! Email ID: {email['id']}")


if __name__ == "__main__":
    to = sys.argv[1] if len(sys.argv) > 1 else TEST_TO
    print(f"テストメール送信先: {to}")
    send_test_email(to)
