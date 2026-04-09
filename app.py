import streamlit as st
import asyncio
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯", layout="wide")

# Style CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION DE NOTIFICATION TELEGRAM ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Config Telegram manquante.")
        return

    header = f"🚨 *RAPPORT DU SWARM* ({datetime.now().strftime('%H:%M')})\n"
    header += "───────────────────\n"
    
    body = ""
    for res in results:
        emoji = "🔥" if res.confidence > 75 else "⚖️"
        body += f"{emoji} *{res.thematique.upper()}*\n"
        body += f"Verdict: {res.final_verdict} ({res.confidence}%)\n"
        body += f"📍 {res.recommendation}\n\n"
    
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": header + body, "parse_mode": "Markdown"},
                      timeout=10)
    except Exception as e:
        print(f"❌ Erreur envoi Telegram: {e}")

# --- LOGIQUE DU PLANIFICATEUR ---
def autonomous_scan_job():
    print(f"⏰ [AUTO] Lancement du scan programmé : {datetime.now()}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(test_swarm())
        if results:
            send_telegram_alert(results)
    finally:
        loop.close()

if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler(daemon=True)
    # 7h et 19h UTC = 9h et 21h France
    scheduler.add_job(autonomous_scan_job, 'cron', hour=7, minute=0)
    scheduler.add_job(autonomous_scan_job, 'cron', hour=19, minute=0)
    scheduler.start()
    st.session_state.scheduler_started = True

# --- INTERFACE UTILISATEUR ---
st.title("🎯 Polymarket Insider Swarm")
st.write("Analyse multi-agents des marchés prédictifs via Groq Llama-3.")

col1, col2, col3 = st.columns(3)
col1.metric("Status", "Opérationnel", "Cloud")
col2.metric("Fréquence", "2 / jour", "Auto")
col3.metric("Mode", "Gratuit", "Optimisé")

st.divider()

if st.button("🚀 LANCER UNE ANALYSE MANUELLE MAINTENANT"):
    with st.spinner("Le Swarm interroge Polymarket..."):
        results = asyncio.run(test_swarm())
        st.session_state.last_results = results
        send_telegram_alert(results)
        st.success("Analyse terminée et envoyée sur Telegram !")

if 'last_results' in st.session_state:
    for res in st.session_state.last_results:
        with st.expander(f"Signal : {res.thematique} ({res.confidence}%)", expanded=True):
            st.write(f"**Verdict :** {res.final_verdict}")
            st.write(f"**Analyse :** {res.summary}")
            st.info(f"**Conseil :** {res.recommendation}")

st.sidebar.title("🛠 Configuration")
st.sidebar.info(f"📡 Scheduler : {'ACTIF' if st.session_state.get('scheduler_started') else 'OFF'}")
st.sidebar.write("Prochains scans : 09:00 & 21:00")