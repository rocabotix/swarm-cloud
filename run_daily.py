import asyncio
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv
from test_swarm import test_swarm
from reporter import generate_daily_report

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def build_html_report(results, session, now):
    rows = ""
    for i, r in enumerate(results):
        color = "#2ecc71" if r.confidence > 65 else "#f39c12" if r.confidence > 40 else "#e74c3c"
        rows += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #333;">{i+1}. {r.thematique}</td>
            <td style="padding:10px;border-bottom:1px solid #333;color:{color};font-weight:bold;">{r.final_verdict}</td>
            <td style="padding:10px;border-bottom:1px solid #333;">{r.confidence}%</td>
            <td style="padding:10px;border-bottom:1px solid #333;">{r.recommendation[:80]}</td>
        </tr>"""
    if not results:
        rows = '<tr><td colspan="4" style="padding:20px;text-align:center;color:#888;">Aucun signal aujourd\'hui</td></tr>'
    return f"""
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial,sans-serif;margin:0;padding:20px;">
    <div style="max-width:700px;margin:auto;background:#16213e;border-radius:12px;padding:30px;">
    <h1 style="color:#00d4ff;text-align:center;">Polymarket Insider Swarm</h1>
    <p style="text-align:center;color:#888;">Session {session} — {now.strftime('%d/%m/%Y %H:%M')} UTC</p>
    <hr style="border-color:#333;margin:20px 0;">
    <h2 style="color:#00d4ff;">Signaux analyses : {len(results)}</h2>
    <table style="width:100%;border-collapse:collapse;">
    <tr style="background:#0f3460;color:#00d4ff;">
        <th style="padding:10px;text-align:left;">Thematique</th>
        <th style="padding:10px;text-align:left;">Verdict</th>
        <th style="padding:10px;text-align:left;">Score</th>
        <th style="padding:10px;text-align:left;">Recommandation</th>
    </tr>
    {rows}
    </table>
<hr style="border-color:#333;margin:20px 0;">
    <p style="color:#888;font-size:12px;text-align:center;">
    Rapport genere automatiquement par Polymarket Insider Swarm.<br>
    Ce rapport ne constitue pas un conseil financier.
    </p>
    </div></body></html>"""

def send_email(subject, html_body, text_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email HTML envoye avec succes")
    except Exception as e:
        print(f"Erreur envoi email: {e}")

async def run_daily():
    now = datetime.now(timezone.utc)
    session = "matin" if now.hour < 12 else "soir"
    print(f"Lancement session {session} - {now.strftime('%Y-%m-%d %H:%M UTC')}")
    results = await test_swarm()
    text_report = generate_daily_report(results)
    html_report = build_html_report(results, session, now)
    subject = f"Polymarket Swarm - Rapport {session} {now.strftime('%d/%m/%Y')}"
    send_email(subject, html_report, text_report)
    print("Session terminee")

if __name__ == "__main__":
    asyncio.run(run_daily())