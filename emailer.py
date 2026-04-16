import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date


def _build_html(items: list[dict]) -> str:
    today = date.today().strftime("%Y년 %m월 %d일")

    rows_by_category: dict[str, list[dict]] = {}
    for item in items:
        rows_by_category.setdefault(item["category"], []).append(item)

    sections = ""
    for category, cat_items in rows_by_category.items():
        rows_html = ""
        for item in cat_items:
            rows_html += f"""
            <tr>
              <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;">
                <a href="{item['url']}" style="color:#1d4ed8;text-decoration:none;">{item['title']}</a>
              </td>
              <td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;white-space:nowrap;color:#6b7280;">
                {item['date']}
              </td>
            </tr>"""

        sections += f"""
        <h2 style="font-size:16px;color:#1e3a5f;margin:24px 0 8px;">{category}</h2>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#f3f4f6;">
              <th style="padding:8px 12px;text-align:left;color:#374151;">제목</th>
              <th style="padding:8px 12px;text-align:left;color:#374151;white-space:nowrap;">등록일</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>"""

    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"></head>
<body style="font-family:'Malgun Gothic',Arial,sans-serif;max-width:700px;margin:0 auto;padding:20px;color:#111;">
  <div style="background:#1e3a5f;padding:20px 24px;border-radius:8px 8px 0 0;">
    <h1 style="margin:0;font-size:18px;color:#fff;">금융감독원 비조치의견서·법령해석 신규 알림</h1>
    <p style="margin:4px 0 0;font-size:13px;color:#93c5fd;">{today} 기준</p>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:20px 24px;border-radius:0 0 8px 8px;">
    {sections}
    <hr style="margin-top:32px;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#9ca3af;margin-top:8px;">
      원문 출처: <a href="https://www.fss.or.kr" style="color:#6b7280;">금융감독원 (fss.or.kr)</a>
    </p>
  </div>
</body>
</html>"""
    return html


def _build_text(items: list[dict]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"금융감독원 신규 알림 ({today})\n" + "=" * 50]
    for item in items:
        lines.append(f"[{item['category']}] {item['title']} ({item['date']})\n  {item['url']}")
    return "\n\n".join(lines)


def send_email(items: list[dict]) -> None:
    """
    환경변수에서 설정을 읽어 이메일 발송.

    필수 환경변수:
      FSS_EMAIL_SENDER    — 발신 Gmail 주소
      FSS_EMAIL_PASSWORD  — Gmail 앱 비밀번호 (16자리)
      FSS_EMAIL_RECIPIENTS — 수신자 이메일 (쉼표 구분, 여러 명 가능)
    """
    sender = os.environ["FSS_EMAIL_SENDER"]
    password = os.environ["FSS_EMAIL_PASSWORD"]
    recipients_raw = os.environ["FSS_EMAIL_RECIPIENTS"]
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    if not items:
        print("신규 항목 없음 — 이메일 발송 생략")
        return

    today = date.today().strftime("%Y.%m.%d")
    subject = f"[FSS 알림] 비조치의견서·법령해석 신규 {len(items)}건 ({today})"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(_build_text(items), "plain", "utf-8"))
    msg.attach(MIMEText(_build_html(items), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"이메일 발송 완료 → {recipients} ({len(items)}건)")
