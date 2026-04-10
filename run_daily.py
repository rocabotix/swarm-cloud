import asyncio
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

from test_swarm import test_swarm
from reporter import generate_daily_report, send_telegram_report

load_dotenv()

def build_html_report(results, session_name, now):
    rows = ""
    for i, r in enumerate(results):
        color = "#2ecc71" if r.confidence > 70 else "#f39c12" if r.confidence > 50 else "#e74c3c"
        debat_html = "".join([f"<p style='color:#3498db;font-size:12px;'>{arg}</p>" for arg in r.key_arguments])

        rows += f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #444;"><b>{r.thematique}</b></td>
            <td style="padding:10px; border-bottom:1px solid #444; color:{color};">{r.final_verdict} ({r.confidence}%)</td>
            <td style="padding:10px; border-bottom:1px solid #444;">{debat_html}</td>
        </tr>"""

    return f"<html><body style='background:#1a1a1a; color:#eee; padding:20px;'><h2>Rapport Swarm {session_name}</h2><table style='width:100%;'>{rows}</table></body></html>"

async def run_daily_session():
    now = datetime.now(timezone.utc)
    session = "Matin" if now.hour < 12 else "Soir"
    
    try:
        results = await test_swarm()
        
        # Envoi Telegram
        report_text = generate_daily_report(results)
        send_telegram_report(report_text)
        
        # Envoi Email
        html_report = build_html_report(results, session, now)
        # (La fonction send_email reste la même que celle de ton fichier d'origine)
        print(f"✅ Session {session} terminée.")
    except Exception as e:
        print(f"💥 Erreur session: {e}")

if __name__ == "__main__":
    asyncio.run(run_daily_session())