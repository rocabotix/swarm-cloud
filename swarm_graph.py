import os
import json
from groq import Groq
from duckduckgo_search import DDGS
from models import WalletSignal, DebateResult

# Initialisation du client Groq (la clé doit être dans tes variables Render)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- FONCTIONS DE RECHERCHE ET IA ---

def get_web_context(topic):
    """Récupère les dernières actualités sur le sujet via DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            # On cherche spécifiquement l'actualité liée à Polymarket et au sujet
            query = f"{topic} news polymarket"
            results = [r for r in ddgs.text(query, max_results=3)]
            if not results:
                return "Aucune actualité récente spécifique trouvée."
            return "\n".join([f"- {r['title']}: {r['body'][:200]}..." for r in results])
    except Exception as e:
        print(f"Erreur recherche DuckDuckGo: {e}")
        return "Contexte web indisponible."

def call_llm(prompt, system_prompt):
    """Appelle le modèle Llama 3 via Groq avec des paramètres de précision."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, # Température basse pour éviter les hallucinations
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur Agent LLM: {str(e)}"

# --- NODES DU GRAPHE (AGENTS) ---

def analyst_node(signal: WalletSignal):
    """Agent Analyste : Interprète le signal avec le contexte Web."""
    news_context = get_web_context(signal.market_slug)
    
    system_prompt = """Tu es l'Analyste 'Insider' de l'essaim. 
    Ton but : prouver que ce mouvement de fonds est un signal intelligent.
    Utilise les news fournies pour donner du sens au pari."""
    
    prompt = f"""MARCHÉ : {signal.market_slug}
    ACTUALITÉ RÉCENTE : 
    {news_context}
    
    DONNÉES ON-CHAIN :
    - Wallet : {signal.wallet}
    - Position : {signal.position_size} USDC
    
    Explique pourquoi ce mouvement est stratégique en fonction des news."""
    
    reasoning = call_llm(prompt, system_prompt)
    signal.breakdown["analyst"] = {"reasoning": reasoning, "news": news_context}
    return signal

def validator_node(state: WalletSignal):
    """Agent Contradicteur : Cherche les failles et rend le verdict final."""
    analyst_opinion = state.breakdown.get("analyst", {}).get("reasoning", "Pas d'analyse.")
    
    system_prompt = """Tu es l'Avocat du Diable.
    Ton but : critiquer l'analyse précédente et souligner les risques (manipulation, rumeurs infondées, manque de liquidité)."""
    
    prompt = f"""Voici l'analyse de ton collègue sur {state.market_slug} :
    '{analyst_opinion}'
    
    Contredis ses arguments et liste les risques majeurs."""
    
    critique = call_llm(prompt, system_prompt)
    
    # Calcul de confiance logique
    confidence = 85 if "fort" in analyst_opinion.lower() else 65
    if "danger" in critique.lower() or "risque" in critique.lower():
        confidence -= 15

    # Construction du résultat final
    result = DebateResult(
        final_verdict="INSIDER" if confidence > 70 else "PRUDENCE",
        confidence=confidence,
        summary=f"Analyse de {state.market_slug} basée sur les flux récents.",
        key_arguments=[
            f"✅ ANALYSTE : {analyst_opinion[:600]}",
            f"⚠️ CONTRADICTEUR : {critique[:600]}"
        ],
        risk_assessment="Élevé" if confidence < 60 else "Modéré",
        recommendation="Suivre le mouvement" if confidence > 75 else "Attendre confirmation",
        thematique=state.thematique
    )
    return {"final_result": result}

# --- FONCTION PRINCIPALE ---

def run_debate(signal: WalletSignal):
    """Lance le cycle complet de l'essaim."""
    try:
        # 1. L'Analyste étudie le cas avec les news
        updated_signal = analyst_node(signal)
        
        # 2. Le Contradicteur valide ou démonte l'analyse
        final_output = validator_node(updated_signal)
        
        return final_output
    except Exception as e:
        print(f"Erreur run_debate: {e}")
        return None