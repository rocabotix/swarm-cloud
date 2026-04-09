import streamlit as st
import asyncio
import os
import requests
from datetime import datetime, timezone
from test_swarm import test_swarm

# --- CONFIGURATION TELEGRAM ---
def send_telegram_alert(results):
    """Envoie le rapport final sur Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        st.warning("⚠️ Configuration Telegram manquante (Token ou Chat ID).")
        return

    message = "🚨 *NOUVELLE ANALYSE DU SWARM* 🚨\n\n"
    for res in results:
        message += f"📌 *{res.thematique.upper()}*\n"
        message += f"Verdict: {res.final_verdict} ({res.confidence}%)\n"
        
        # On ajoute le résumé du débat dans le Telegram
        if hasattr(res, 'key_arguments') and res.key_arguments:
            for arg in res.key_arguments:
                # On limite la taille pour Telegram
                message += f"{arg[:200]}...\n"
        
        message += "-------------------\n"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id, 
            "text": message, 
            "parse_mode": "Markdown"
        }, timeout=10)
    except Exception as e:
        st.error(f"Erreur d'envoi Telegram : {e}")

# --- CONFIGURATION INTERFACE STREAMLIT ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯", layout="wide")

st.title("🎯 Polymarket Insider Swarm")
st.caption("Intelligence Artificielle multi-agents synchronisée sur les flux Polymarket")

# Initialisation des états
if "results" not in st.session_state:
    st.session_state.results = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None

# --- SECTION ACTIONS ---
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🚀 Lancer l'Analyse", type="primary"):
        with st.spinner("Le Swarm interroge Polymarket et Google News..."):
            try:
                # Exécution de la logique Swarm (test_swarm contient la boucle de scan)
                results = asyncio.run(test_swarm())
                st.session_state.results = results
                st.session_state.last_run = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                
                if results:
                    send_telegram_alert(results)
                    st.success(f"Analyse terminée avec succès à {st.session_state.last_run}")
                else:
                    st.info("Scan effectué : Aucun mouvement suspect détecté.")
            except Exception as e:
                st.error(f"Erreur système : {e}")

# --- AFFICHAGE DES RÉSULTATS ---
st.divider()

if st.session_state.results:
    st.subheader(f"📊 Derniers Signaux ({st.session_state.last_run})")
    
    for i, result in enumerate(st.session_state.results):
        # Création d'une carte extensible pour chaque thématique
        with st.expander(f"{i+1}. {result.thematique} — Verdict: {result.final_verdict} ({result.confidence}%)", expanded=True):
            
            # Layout en colonnes pour les détails
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                st.metric("Confiance", f"{result.confidence}%")
                st.write("**Risque :**", result.risk_assessment)
            with c2:
                st.write("**📝 Résumé :**")
                st.write(result.summary)
            with c3:
                st.write("**💡 Recommandation :**")
                st.info(result.recommendation)
            
            # --- SECTION DÉBAT DES AGENTS ---
            st.markdown("---")
            st.markdown("🔍 **DÉBAT INTERNE DES AGENTS**")
            
            if hasattr(result, 'key_arguments') and result.key_arguments:
                for arg in result.key_arguments:
                    if "✅" in arg:
                        st.info(arg)  # Bleu pour l'Analyste
                    elif "⚠️" in arg:
                        st.warning(arg)  # Orange pour le Contradicteur
                    else:
                        st.write(arg)
            else:
                st.write("Détails du débat indisponibles pour ce signal.")

else:
    st.info("En attente de lancement. Cliquez sur le bouton pour scanner le marché.")

# Pied de page
st.divider()
st.caption("Flux de données : Polymarket Data API | Recherche : DuckDuckGo | Cerveau : Llama 3.3 70B")