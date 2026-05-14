import asyncio
import os
import requests
from dataclasses import dataclass
from typing import List
from groq import Groq

# --- CONFIGURATION DU CLIENT ---
# Assure-toi que la variable d'environnement GROQ_API_KEY est bien configurée sur Render
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
    Récupère les données réelles de Polymarket et les analyse avec le bon modèle LLM.
    """
    raw_markets = []
    
    # 1. RÉCUPÉRATION DES DONNÉES RÉELLES (API GAMMA POLYMARKET)
    try:
        url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erreur API Polymarket : Code {response.status_code}")
            return []

        data = response.json()
        print(f"📡 [DEBUG] {len(data)} événements reçus de Polymarket.")

        for event in data:
            title = event.get('title', 'Titre inconnu')
            markets_list = event.get('markets', [])
            
            if markets_list:
                m = markets_list[0]
                
                try:
                    # Extraction et conversion des données financières
                    v = float(m.get('volume', 0))
                    l = float(m.get('liquidity', 1))
                    l = l if l > 0 else 1
                    ratio = v / l
                except Exception:
                    v, l, ratio = 0, 1, 0
                
                # On ne garde que les marchés avec un minimum d'activité pour l'analyse
                if v > 100:
                    raw_markets.append({
                        "title": title,
                        "volume": v,
                        "liquidity": l,
                        "ratio": ratio
                    })

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données : {e}")
        return []

    # 2. FILTRAGE ET TRI
    # On trie par volume pour analyser les sujets les plus importants
    raw_markets = sorted(raw_markets, key=lambda x: x['volume'], reverse=True)
    
    # Sélection des 3 premières anomalies ou gros volumes
    target_markets = raw_markets[:3]

    if not target_markets:
        print("🔍 Aucun marché éligible trouvé.")
        return []

    results = []

    # 3. ANALYSE PAR LE SWARM D'AGENTS
    for market in target_markets:
        title = market['title']
        v = market['volume']
        l = market['liquidity']
        r = market['ratio']

        print(f"🧠 [IA] Analyse en cours : {title} (Ratio: {r:.2f})")

        try:
            # --- UTILISATION DU BON MODÈLE : llama-3.3-70b-versatile ---
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es une équipe d'analystes spécialisés en détection d'Insider Trading et de manipulation de marché (Wash Trading). Ton ton est froid, analytique et impartial."
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyse le marché suivant : '{title}'.
                        Données financières :
                        - Volume total : ${v:,.2f}
                        - Liquidité disponible : ${l:,.2f}
                        - Ratio Volume/Liquidité : {r:.2f}
                        
                        Débats sur la probabilité que ce volume cache une information privilégiée ou une manipulation technique. Donne un verdict final court."""
                    }
                ],
                model="llama-3.3-70b-versatile", 
                temperature=0.2,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Calcul dynamique du score de confiance
            conf_base = 70
            conf = min(95, int(conf_base + (r * 2))) if r > 1 else conf_base

            results.append(SwarmResult(
                thematique=title,
                final_verdict="ACCUMULATION / INSIDER" if r > 2 else "FLUX ORGANIQUE",
                confidence=conf,
                summary=analysis_text,
                recommendation="Vérifier les flux on-chain" if r > 2 else "Attendre confirmation",
                key_arguments=[f"Ratio asymétrique : {r:.2f}"],
                risk_assessment="ÉLEVÉ" if r > 5 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(3.0, r):.1f}%" if conf > 80 else "Observer"
            ))
            
        except Exception as e:
            print(f"⚠️ Erreur critique lors de l'appel Groq pour {title} : {e}")
            continue

    return results

# --- BLOC DE TEST ---
if __name__ == "__main__":
    # Test local : python test_swarm.py
    res = asyncio.run(test_swarm())
    for r in res:
        print(f"\n✅ {r.thematique} -> {r.final_verdict} ({r.confidence}%)")