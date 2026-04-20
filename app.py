import streamlit as st
import asyncio
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from test_swarm import test_swarm

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Polymarket Insider Swarm", 
    page_icon="🎯", 
    layout="wide"
)

# Style CSS personnalisé pour un look "Terminal Trading"
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        height: 3.5em; 
        background-color: #ff4b4b; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #ff3333; border: 1px solid white; }
    .metric-container { background-color: #1e212b; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION D'ENVOI TELEGRAM ---
def send_telegram_alert(results):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        st.warning("⚠️ Variables Telegram manquantes dans l'onglet Environment de Render.")
        return

    for res in results:
        priority = "🚨 HAUTE PRIORITÉ" if res.confidence > 85 else "📡 SIGNAL"
        
        message = f"{priority}\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"🎯 **MARCHÉ :** {res.thematique.upper()}\n\n"
        message += f"💰 **ACTION :** {res.final_verdict}\n"
        message += f"📊 **CONFIANCE :** {res.confidence}%\n"
        message += f"⚖️ **STRATÉGIE :** {res.kelly_criterion}\n\n"
        message += f"🔎 **POURQUOI :**\n{res.summary[:300]}...\n\n"
        message += f"⚠️ **RISQUE :** {res.risk_assessment}\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"🔗 [Ouvrir Polymarket](https://polymarket.com/)"

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id, 
                "text": message, 
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            st.error(f"Erreur d'envoi Telegram : {e}")

# --- LOGIQUE DU PLANIFICATEUR (SCHEDULER) ---
def autonomous_scan_job():
    """Fonction exécutée par le scheduler à heures fixes"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # On lance le scan
        results = loop.run_until_complete(test_swarm())
        if results:
            send_telegram_alert(results)
    except Exception as e:
        print(f"Erreur Scheduler : {e}")
    finally:
        loop.close()

# Initialisation du Scheduler une seule fois
if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler(daemon=True)
    # Scan à 09:00 et 21:00 (Heure FR si UTC+2 sur Render, donc 07:00 et 19:00 UTC)
    scheduler.add_job(autonomous_scan_job, 'cron', hour=7, minute=0)
    scheduler.add_job(autonomous_scan_job, 'cron', hour=19, minute=0)
    scheduler.start()
    st.session_state.scheduler_started = True

# --- INTERFACE UTILISATEUR STREAMLIT ---
st.title("🎯 Swarm Insider Trading")
st.subheader("Détection d'anomalies sur les marchés de niche")

# Métriques en haut de page
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Statut", "Opérationnel", "LIVE")
with m_col2:
    st.metric("Modèle IA", "Llama 3.3-70B")
with m_col3:
    st.metric("Filtre", "Exclusion Crypto/GTA", delta_color="normal")

st.divider()

# Bouton de lancement manuel
if st.button("🚀 LANCER UNE ANALYSE MANUELLE MAINTENANT"):
    with st.spinner("Le Swarm analyse les volumes et la liquidité..."):
        try:
            results = asyncio.run(test_swarm())
            st.session_state.last_results = results
            
            # Envoi Telegram
            send_telegram_alert(results)
            st.success(f"Analyse terminée. {len(results)} signaux trouvés.")
        except Exception as e:
            st.error(f"Erreur lors de l'exécution : {e}")

# Affichage des résultats sur l'interface
if 'last_results' in st.session_state and st.session_state.last_results:
    st.markdown("### 📊 Derniers Signaux Détectés")
    
    for res in st.session_state.last_results:
        # Couleur dynamique selon la confiance
        header_color = "red" if res.confidence > 80 else "orange"
        
        with st.expander(f"MARCHÉ : {res.thematique.upper()} ({res.confidence}%)", expanded=True):
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.markdown(f"**Verdict :** :{header_color}[{res.final_verdict}]")
                st.write(f"**Analyse du Swarm :**\n{res.summary}")
            
            with c2:
                st.warning(f"**Risque :** {res.risk_assessment}")
                st.info(f"**Stratégie :**\n{res.kelly_criterion}")
                st.write(f"**Indicateur :** {res.recommendation}")
            
            st.markdown(f"[🔗 Lien direct vers le marché](https://polymarket.com/)")
else:
    st.info("Aucune donnée récente. Cliquez sur le bouton ci-dessus pour scanner les marchés Polymarket.")

# Pied de page
st.divider()
st.caption(f"Dernière actualisation de l'interface : {datetime.now().strftime('%H:%M:%S')}")