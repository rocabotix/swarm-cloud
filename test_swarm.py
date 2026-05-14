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
        # On cible les marchés actifs et populaires
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
                
                # Conversion sécurisée en float (l'API peut envoyer du string)
                try:
                    v = float(m.get('volume', 0))
                    l = float(m.get('liquidity', 1))
                    # On évite la division par zéro
                    l = l if l > 0 else 1
                    ratio = v / l
                except:
                    v, l, ratio = 0, 1, 0
                
                # On ne prend que les marchés avec un minimum d'activité
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
    # On trie par volume décroissant pour être sûr d'avoir des vrais sujets
    # On ne filtre PAS par ratio pour ce test, pour forcer l'affichage
    raw_markets = sorted(raw_markets, key=lambda x: x['volume'], reverse=True)
    
    # On prend les 5 premiers pour l'analyse
    target_markets = raw_markets[:5]

    if not target_markets:
        print("🔍 Aucun marché avec volume > 100 trouvé.")
        return []

    results = []

    # 3. ANALYSE PAR LE SWARM
    for market in target_markets[:3]: # On analyse les 3 plus gros
        title = market['title']
        v = market['volume']
        l = market['liquidity']
        r = market['ratio']

        print(f"🧠 [IA] Analyse en cours : {title} (Ratio: {r:.2f})")

        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es une équipe d'analystes spécialisés en Insider Trading (Swarm). Sois précis et technique."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyse : '{title}'. Volume: ${v} | Liq: ${l} | Ratio: {r:.2f}. Débats sur la probabilité d'insider trading ou de wash trading. Verdict court."
                    }
                ],
                model="llama-3.3-70b-specdec",
                temperature=0.2,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Score de confiance dynamique
            conf = min(95, int(60 + (r * 5)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="ACCUMULATION" if r > 1.2 else "FLUX NEUTRE",
                confidence=conf,
                summary=analysis_text,
                recommendation="Surveiller les carnets d'ordres" if r > 1.2 else "Attendre",
                key_arguments=[f"Ratio Vol/Liq de {r:.2f}"],
                risk_assessment="ÉLEVÉ" if r > 2 else "MODÉRÉ",
                kelly_criterion=f"Mise {min(3, r):.1f}%" if conf > 75 else "Observer"
            ))
            
        except Exception as e:
            print(f"⚠️ Erreur IA sur {title}: {e}")
            continue

    return results

# --- TEST LOCAL ---
if __name__ == "__main__":
    res = asyncio.run(test_swarm())
    for r in res:
        print(f"\n✅ {r.thematique} -> {r.final_verdict}")