import asyncio
import os
from dataclasses import dataclass
from typing import List
from groq import Groq

# --- CONFIGURATION DU CLIENT ---
# Assure-toi que la variable d'environnement GROQ_API_KEY est bien configurée
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@dataclass
class SwarmResult:
    thematique: str
    final_verdict: str
    confidence: int
    summary: str
    recommendation: str
    key_arguments: List[str]
    risk_assessment: str
    kelly_criterion: str

async def test_swarm():
    """
    Analyse les marchés, filtre les bruits (GTA, BTC, etc.) 
    et détecte les anomalies de volume via le Swarm d'IA.
    """
    
    # 1. DONNÉES DE MARCHÉ (Simulées - À connecter à l'API Polymarket ultérieurement)
    # On simule ici des marchés avec des volumes et de la liquidité pour le calcul de ratio
    raw_markets = [
        {"title": "GTA VI Trailer Release Date", "volume": 1200000, "liquidity": 400000},
        {"title": "US TikTok Ban implementation by August", "volume": 600000, "liquidity": 50000}, # Ratio 12 (Anomalie)
        {"title": "Bitcoin Price hits $100k", "volume": 8000000, "liquidity": 3000000},
        {"title": "New Tech CEO Appointment", "volume": 200000, "liquidity": 15000}, # Ratio 13.3 (Anomalie)
        {"title": "French Election Surprise 2027", "volume": 90000, "liquidity": 70000},
        {"title": "Ethereum ETF Outflows", "volume": 1500000, "liquidity": 800000}
    ]

    # 2. FILTRAGE ANTI-BRUIT (Exclusion des marchés évidents/saturés)
    excluded_keywords = ["GTA", "BITCOIN", "BTC", "ETH", "ETHEREUM", "SOLANA", "SOL", "DOGE"]
    
    filtered_markets = []
    for m in raw_markets:
        title_upper = m['title'].upper()
        if not any(keyword in title_upper for keyword in excluded_keywords):
            filtered_markets.append(m)

    if not filtered_markets:
        return []

    results = []

    # 3. ANALYSE PAR LE SWARM D'AGENTS
    # On prend les 3 meilleurs marchés restants après filtrage
    for market in filtered_markets[:3]:
        title = market['title']
        volume = market['volume']
        liquidity = market['liquidity']
        vol_liq_ratio = volume / liquidity
        
        # Détection d'anomalie quantitative
        is_anomaly = vol_liq_ratio > 2.5 # Seuil arbitraire pour détecter un mouvement suspect

        # Prompt pour le débat des agents (Modèle mis à jour vers llama-3.3)
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es une équipe d'analystes financiers (Swarm). Ton rôle est de détecter l'insider trading. Sois sceptique, froid et ultra-analytique."
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyse le marché : '{title}'. 
                        Données : Volume {volume} | Liquidité {liquidity} | Ratio Vol/Liq : {vol_liq_ratio:.2f}.
                        Anomalie détectée : {'OUI' if is_anomaly else 'NON'}.
                        Fais un débat entre un Analyste (cherche les preuves de smart money) et un Contradicteur (cherche le wash trading).
                        Donne un verdict final court."""
                    }
                ],
                model="llama-3.3-70b-specdec", # LE MODÈLE MIS À JOUR
                temperature=0.2, # Basse température pour plus de précision factuelle
            )
            
            analysis_text = response.choices[0].message.content
            
            # Calcul du score de confiance et du critère de Kelly
            confidence_score = 85 if is_anomaly else 65
            kelly = "Miser 2-3% du capital" if confidence_score > 80 and is_anomaly else "Observer / Pas de mise"

            results.append(SwarmResult(
                thematique=title,
                final_verdict="ACHAT ACCUMULATION" if is_anomaly else "FLUX NORMAL",
                confidence=confidence_score,
                summary=analysis_text,
                recommendation=f"Ratio Vol/Liq de {vol_liq_ratio:.2f}. {'Cibler les entrées' if is_anomaly else 'Attendre'}.",
                key_arguments=["Volume anormal par rapport à la liquidité" if is_anomaly else "Volume organique"],
                risk_assessment="ÉLEVÉ" if is_anomaly else "MODÉRÉ",
                kelly_criterion=kelly
            ))
            
        except Exception as e:
            print(f"Erreur lors de l'analyse du marché {title}: {e}")
            continue

    return results

# --- TEST LOCAL ---
if __name__ == "__main__":
    # Pour tester localement, assure-toi d'avoir fait : export GROQ_API_KEY="ta_cle"
    res_list = asyncio.run(test_swarm())
    for r in res_list:
        print(f"\n--- {r.thematique} ---")
        print(f"Verdict : {r.final_verdict} ({r.confidence}%)")
        print(f"Kelly : {r.kelly_criterion}")
        print(f"Analyse : {r.summary[:200]}...")