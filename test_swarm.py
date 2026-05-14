import asyncio
import os
import requests
from dataclasses import dataclass
from typing import List
from groq import Groq

# --- CONFIGURATION DU CLIENT ---
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
    Scanne Polymarket, traite les données et fait débattre le Swarm.
    """
    raw_markets = []
    
    # 1. RÉCUPÉRATION DES DONNÉES (API GAMMA)
    try:
        # On cible les marchés actifs
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
                
                # Conversion sécurisée en float
                try:
                    v = float(m.get('volume', 0))
                    l = float(m.get('liquidity', 1))
                    l = l if l > 0 else 1
                    ratio = v / l
                except:
                    v, l, ratio = 0, 1, 0
                
                # Seuil minimal pour éviter le spam
                if v > 100:
                    raw_markets.append({
                        "title": title,
                        "volume": v,
                        "liquidity": l,
                        "ratio": ratio
                    })

    except Exception as e:
        print(f"❌ Erreur lors du fetch : {e}")
        return []

    # 2. FILTRAGE ET TRI
    # Tri par volume pour avoir les marchés les plus sérieux
    raw_markets = sorted(raw_markets, key=lambda x: x['volume'], reverse=True)
    
    # On prend les marchés à analyser
    target_markets = raw_markets[:5]

    if not target_markets:
        print("🔍 Aucun marché avec volume > 100 trouvé.")
        return []

    results = []

    # 3. ANALYSE PAR LE SWARM
    for market in target_markets[:3]:
        title = market['title']
        v = market['volume']
        l = market['liquidity']
        r = market['ratio']

        print(f"🧠 [IA] Analyse en cours : {title}")

        try:
            # CORRECTION : Utilisation du modèle 'versatile' (le nouveau standard)
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es une équipe d'analystes spécialisés en Insider Trading (Swarm). Sois précis, sceptique et technique."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyse : '{title}'. Volume: ${v} | Liq: ${l} | Ratio: {r:.2f}. Débats sur la probabilité d'insider trading ou de wash trading. Verdict court."
                    }
                ],
                model="llama-3.3-70b-versatile", 
                temperature=0.2,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Score de confiance dynamique
            conf = min(95, int(65 + (r * 3)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="ACCUMULATION" if r > 1.2 else "FLUX NEUTRE",
                confidence=conf,
                summary=analysis_text,
                recommendation="Surveiller les flux" if r > 1.2 else "Attendre",
                key_arguments=[f"Ratio Vol/Liq de {r:.2f}"],
                risk_assessment="ÉLEVÉ" if r > 2 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(3, r):.1f}%" if conf > 75 else "Observer"
            ))
            
        except Exception as e:
            # Ce bloc va maintenant capturer les erreurs de modèle si Groq change encore
            print(f"⚠️ Erreur IA sur {title}: {e}")
            continue

    return results

# --- TEST LOCAL ---
if __name__ == "__main__":
    res = asyncio.run(test_swarm())
    for r in res:
        print(f"\n✅ {r.thematique} -> {r.final_verdict}")