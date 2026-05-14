import streamlit as st
import asyncio
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Swarm Insider Scanner", page_icon="🚀")

# --- FONCTION D'ENVOI TELEGRAM ---
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ DEBUG TELEGRAM: Token ou Chat ID manquant dans les variables d'environnement.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ DEBUG TELEGRAM: Message envoyé avec succès à {chat_id}")
            return True
        else:
            print(f"❌ DEBUG TELEGRAM: Erreur {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ DEBUG TELEGRAM: Exception lors de l'envoi : {e}")
        return False

# --- FONCTION DE SCAN (UTILISÉE PAR LE BOUTON ET LE SCHEDULER) ---
def run_analysis():
    print(f"📡 [SCAN] Démarrage de l'analyse à {datetime.now()}")
    results = asyncio.run(test_swarm())
    
    if results:
        header = f"🚀 *SWARM REPORT - {datetime.now().strftime('%d/%m %H:%M')}*\n"
        send_telegram_message(header)
        
        for res in results:
            msg = (
                f"📊 *MARCHÉ : {res.thematique}*\n"
                f"Verdict : {res.final_verdict} ({res.confidence}%)\n"
                f"Stratégie : {res.kelly_criterion}\n"
                f"Note : {res.recommendation}\n"
                f"--------------------------"
            )
            send_telegram_message(msg)
        return results
    else:
        print("🔍 [SCAN] Aucun signal trouvé lors du scan.")
        return []

# --- PLANIFICATEUR (SCHEDULER) ---
# S'exécute en arrière-plan
if "scheduler_started" not in st.session_state:
    scheduler = BackgroundScheduler(timezone="Europe/Paris")
    # Planification à 09:00 et 21:00
    scheduler.add_job(run_analysis, 'cron', hour='9,21', minute=0)
    scheduler.start()
    st.session_state.scheduler_started = True
    print("🚀 [SCHEDULER] Le planificateur est démarré (09h/21h Paris).")

# --- INTERFACE STREAMLIT ---
st.title("🚀 Swarm Cloud Predictor")
st.write("Analyse en temps réel des asymétries de volume sur Polymarket.")

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 LANCER UNE ANALYSE MANUELLE"):
        with st.spinner("Le Swarm analyse Polymarket..."):
            results = run_analysis()
            if results:
                st.success(f"Analyse terminée. {len(results)} signaux envoyés à Telegram.")
                for r in results:
                    with st.expander(f"Détails : {r.thematique}"):
                        st.write(f"**Verdict :** {r.final_verdict}")
                        st.write(f"**Confiance :** {r.confidence}%")
                        st.write(f"**Analyse :** {r.summary}")
            else:
                st.warning("Aucun signal trouvé avec les filtres actuels.")

with col2:
    st.write(f"**Heure du serveur :** {datetime.now().strftime('%H:%M:%S')}")

# --- AFFICHAGE DES DERNIERS LOGS DANS L'APP ---
st.divider()
st.subheader("📊 État du Système")
st.info("Le bot scanne automatiquement à 09:00 et 21:00. Les résultats sont envoyés directement sur Telegram.")

if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
    st.success("✅ Configuration Telegram détectée.")
else:
    st.error("❌ Configuration Telegram manquante dans les variables d'environnement Render.")