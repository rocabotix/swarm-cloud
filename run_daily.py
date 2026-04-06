import asyncio
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

# Import de tes modules locaux
from test_swarm import test_swarm
from reporter import generate_daily_report, send_telegram_report

load_dotenv()

# Configuration Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def build_html_report(results, session_name, now):
    """Génère un rapport HTML élégant pour l'envoi par Email"""
    rows = ""
    for i, r in enumerate(results):
        # Couleur selon la confiance
        color = "#2ecc71" if r.confidence > 70 else "#f39c12" if r.confidence > 50 else "#e74c3c"
        
        # Extraction du débat pour l'email
        debat_html = ""
        if hasattr(r, 'key_arguments') and r.key_arguments:
            for arg in r.key_arguments:
                if "CONTRADICTEUR" in arg.upper() or "⚠️" in arg:
                    debat_html += f"<p style='color:#e74c3c;font-size:12px;margin:2px 0;'><i>{arg}</i></p>"
                else:
                    debat_html += f"<p style='color:#3498db;font-size:12px;margin:2px 0;'>{arg}</p>"

        rows += f"""
        <tr>
            <td style="padding:15px; border-bottom:1px solid #444;">
                <b style="color:#fff;">{i+1}. {r.thematique}</b><br>
                <span style="font-size:12px; color:#bbb;">{r.summary}</span>
            </td>
            <td style="padding:15px; border-bottom:1px solid #444; color:{color}; font-weight:bold; text-align:center;">
                {r.final_verdict}<br><small>{r.confidence}%</small>
            </td>
            <td style="padding:15px; border-bottom:1px solid #444;">
                {debat_html}
            </td>
        </tr>"""

    if not results:
        rows = "<tr><td colspan='3' style='padding:20px; text-align:center; color:#888;'>Aucun signal détecté.</td></tr>"

    html = f"""
    <html>
    <body style="font-family:Arial, sans-serif; background-color:#1a1a1a; color:#eee; padding:20px;">
        <div style="max-width:800px; margin:auto; background:#252525; border-radius:10px; padding:20px; border:1px solid #333;">
            <h2 style="color:#00ffa3; text-align:center;">🎯 Polymarket Insider Swarm</h2>
            <p style="text-align:center; color:#888;">Rapport de session : <b>{session_name.upper()}</b> | {now.strftime('%d/%m/%Y %H:%M UTC')}</p>
            
            <table style="width:100%; border-collapse:collapse; margin-top:20px;">
                <thead>
                    <tr style="background:#333; color:#00ffa3;">
                        <th style="padding:10px; text-align:left;">Marché</th>
                        <th style="padding:10px; text-align:center;">Verdict</th>
                        <th style="padding:10px; text-align:left;">Détails Agents</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            
            <p style="font-size:11px; color:#666; margin-top:30px; text-align:center;">
                Généré par votre infrastructure autonome Render & Groq.<br>
                Ceci n'est pas un conseil financier.
            </p>
        </div>
    </body>
    </html>
    """
    return html

def send_email(subject, html_body):
    """Envoie le rapport par Email"""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("⚠️ Email non configuré, saut de l'étape.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Email envoyé avec succès")
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")

async def run_daily_session():
    """Fonction principale appelée par le scheduler ou manuellement"""
    now = datetime.now(timezone.utc)
    session = "Matin" if now.hour < 12 else "Soir"
    
    print(f"🚀 Lancement du Swarm - Session {session} ({now.strftime('%H:%M UTC')})")
    
    try:
        # 1. Lancement de l'analyse (Swarm)
        results = await test_swarm()
        
        # 2. Génération et envoi du rapport Telegram (Détaillé)
        report_text = generate_daily_report(results)
        send_telegram_report(report_text)
        
        # 3. Génération et envoi du rapport Email (Visuel)
        html_report = build_html_report(results, session, now)
        subject = f"🎯 Rapport Swarm Polymarket - {session} {now.strftime('%d/%m')}"
        send_email(subject, html_report)
        
        print(f"✅ Session {session} terminée avec succès.")
        
    except Exception as e:
        print(f"💥 Erreur critique lors de la session daily: {e}")

if __name__ == "__main__":
    asyncio.run(run_daily_session())