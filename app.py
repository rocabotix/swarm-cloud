import streamlit as st
import asyncio
import os
import requests
from datetime import datetime, timezone
from test_swarm import test_swarm

# --- CONFIGURATION TELEGRAM ---
def send_telegram_alert(results):
    # Support des deux noms de variables pour éviter les erreurs Render
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        return

    message = "🚨 **NOUVELLE ANALYSE DU SWARM** 🚨\n\n"
    for res in results:
        # On affiche tout ce qui a au moins 50% de confiance pour le test
        if res.confidence >= 50:
            message += f"🎯 *{res.thematique.upper()}*\n"
            message += f"Verdict: {res.final_verdict} ({res.confidence}%)\n"
            
            # Ajout du débat dans Telegram aussi
            if res.key_arguments:
                for arg in res.key_arguments:
                    message += f"{arg}\n"
            
            message += "-------------------\n"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Erreur Telegram: {e}")

# --- CONFIGURATION PAGE STREAMLIT ---
st.set_page_config(page_title="Polymarket Insider Swarm", page_icon="🎯", layout="wide")

st.title("🎯 Polymarket Insider Swarm")
st.caption("Analyse multi-agents des flux de portefeuilles Polymarket")

if "results" not in st.session_state:
    st.session_state.results = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None

# --- BOUTON D'ACTION ---
if st.button("Lancer une analyse", type="primary"):
    with st.spinner("L'essaim analyse les marchés en cours..."):
        try:
            # Exécution du swarm
            results = asyncio.run(test_swarm())
            st.session_state.results = results
            st.session_state.last_run = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            
            if results:
                send_telegram_alert(results)
                st.success(f"Analyse terminée ! {len(results)} signaux traités.")
            else:
                st.info("Aucun mouvement significatif détecté actuellement.")
        except Exception as e:
            st.error(f"Erreur lors de l'exécution du Swarm : {e}")

st.divider()

# --- AFFICHAGE DES RÉSULTATS DÉTAILLÉS ---
if st.session_state.results:
    if st.session_state.last_run:
        st.write(f"⏱️ Dernière mise à jour : {st.session_state.last_run}")

    for i, result in enumerate(st.session_state.results):
        # Header de l'expander
        label = f"{i+1}. {result.thematique} — {result.final_verdict} ({result.confidence}%)"
        
        with st.expander(label):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🛡️ Verdict :**", result.final_verdict)
                st.write("**📊 Confiance :**", f"{result.confidence}%")
            with col2:
                st.write("**📝 Résumé :**", result.summary)
                st.write("**💡 Reco :**", result.recommendation)
            
            # --- AFFICHAGE DU DÉBAT DES AGENTS ---
            if hasattr(result, 'key_arguments') and result.key_arguments:
                st.markdown("---")
                st.subheader("🕵️ Débat des Agents (Analyste vs Contradicteur)")
                for arg in result.key_arguments:
                    if "✅" in arg:
                        st.info(arg)      # Style Bleu pour l'Analyste
                    elif "⚠️" in arg:
                        st.warning(arg)   # Style Orange pour le Contradicteur
                    else:
                        st.write(arg)     # Texte normal pour le reste