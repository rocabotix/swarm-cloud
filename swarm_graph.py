import json
from groq import Groq
from models import WalletSignal, DebateResult
from config import GROQ_API_KEY

# Initialisation du client Groq
client = Groq(api_key=GROQ_API_KEY)

# --- CONFIGURATION DES AGENTS (PROMPTS) ---

SYSTEM_ANALYST = """Tu es l'Analyste 'Insider' du Swarm Polymarket. 
Ton rôle est de trouver des preuves qu'un mouvement de portefeuille est un signal d'achat intelligent (Smart Money).
Concentre-toi sur : 
1. La taille de la position.
2. L'historique du wallet (Est-ce un habitué ou un nouveau compte suspect ?).
3. La pertinence du pari par rapport à la thématique.
RESTE STRICTEMENT CONCENTRÉ SUR LES DONNÉES FOURNIES. Ne parle pas d'autres sujets."""

SYSTEM_CONTRADICTEUR = """Tu es l'Avocat du Diable (Le Contradicteur). 
Ton unique but est de critiquer l'analyse de l'Analyste et de trouver des risques.
Cherche :
1. Les risques de manipulation (Wash Trading).
2. Le manque de liquidité du marché.
3. Les facteurs externes que l'analyste ignore (News, blessures, délais).
Sois sceptique, pessimiste et direct. Ne sois jamais d'accord par défaut."""

# --- FONCTIONS UTILITAIRES ---

def call_llm(prompt, system_prompt):
    """Appelle le LLM avec un système strict pour éviter les mélanges de thématiques."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Température basse pour éviter les hallucinations/mélanges
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur agent : {str(e)}"

# --- NODES DU GRAPHE ---

def analyst_node(signal: WalletSignal):
    """Premier agent : Analyse le signal positivement."""
    prompt = f"""Analyse ce signal On-Chain pour le marché '{signal.market_slug}' :
    - Wallet: {signal.wallet}
    - Taille Position: {signal.position_size} USDC
    - Âge du compte: {signal.age_days} jours
    - Thématique: {signal.thematique}
    
    Explique pourquoi c'est un signal intéressant."""
    
    reasoning = call_llm(prompt, SYSTEM_ANALYST)
    signal.breakdown["analyst"] = {"reasoning": reasoning}
    return signal

def validator_node(state: WalletSignal):
    """Deuxième agent : Contredit l'analyse et génère le résultat final."""
    analyst_opinion = state.breakdown.get("analyst", {}).get("reasoning", "Pas d'analyse disponible.")
    
    prompt = f"""Voici l'analyse positive de mon collègue pour le marché '{state.market_slug}' :
    ---
    {analyst_opinion}
    ---
    Trouve les failles et les risques majeurs liés à ce pari et à ce wallet précis. 
    Ne parle QUE de ce marché ({state.market_slug})."""
    
    critique = call_llm(prompt, SYSTEM_CONTRADICTEUR)
    
    # Calcul d'un score de confiance simplifié
    confidence_score = 75
    if "RISQUE ÉLEVÉ" in critique.upper() or "DANGER" in critique.upper():
        confidence_score = 55

    # Création du résultat final structuré pour app.py et reporter.py
    result = DebateResult(
        final_verdict="INSIDER" if confidence_score > 70 else "SUIVRE AVEC PRUDENCE",
        confidence=confidence_score,
        summary=f"Analyse du wallet {state.wallet[:8]}... sur {state.market_slug}",
        key_arguments=[
            f"✅ ANALYSTE : {analyst_opinion[:500]}...",
            f"⚠️ CONTRADICTEUR : {critique[:500]}..."
        ],
        risk_assessment="Élevé" if confidence_score < 60 else "Modéré",
        recommendation="Vérifier la liquidité avant d'entrer." if confidence_score < 70 else "Signal fort, surveiller les mouvements du wallet.",
        thematique=state.thematique
    )
    
    return {"final_result": result}

# --- POINT D'ENTRÉE DU SWARM ---

def run_debate(signal: WalletSignal):
    """Orchestre le débat entre l'Analyste et le Contradicteur."""
    try:
        # Étape 1 : Analyse
        state_after_analyst = analyst_node(signal)
        
        # Étape 2 : Contradiction et Verdict
        final_output = validator_node(state_after_analyst)
        
        return final_output
    except Exception as e:
        print(f"Erreur dans le cycle run_debate: {e}")
        return None