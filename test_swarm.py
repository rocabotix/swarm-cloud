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
    Scanne les vrais marchés de Polymarket, filtre les bruits
    et analyse les anomalies de volume via Llama 3.3.
    """
    
    raw_markets = []
    
    # 1. RÉCUPÉRATION DES DONNÉES RÉELLES (Gamma API Polymarket)
    try:
        # On récupère les 100 marchés les plus actifs
        url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        for event in data:
            title = event.get('title', '')
            markets_list = event.get('markets', [])
            
            if markets_list:
                # On prend le premier marché de l'événement (souvent le principal)
                m = markets_list[0]
                
                # Extraction des métriques
                # La liquidité est souvent représentée par 'liquidity' ou le 'groupScore'
                volume = float(m.get('volume', 0))
                liquidity = float(m.get('liquidity', 1)) # On évite la division par zéro
                
                if volume > 500: # On ignore les micro-marchés sans intérêt
                    raw_markets.append({
                        "title": title,
                        "volume": volume,
                        "liquidity": liquidity
                    })
    except Exception as e:
        print(f"❌ Erreur API Polymarket: {e}")
        return []

    # 2. FILTRAGE ANTI-BRUIT
    excluded_keywords = ["GTA", "BITCOIN", "BTC", "ETH", "ETHEREUM", "SOLANA", "SOL", "DOGE"]
    
    filtered_markets = []
    for m in raw_markets:
        title_upper = m['title'].upper()
        if not any(keyword in title_upper for keyword in excluded_keywords):
            # Calcul du ratio
            ratio = m['volume'] / m['liquidity'] if m['liquidity'] > 0 else 0
            m['ratio'] = ratio
            # On ne garde que si le ratio est suspect (> 1.5)
            if ratio > 1.5:
                filtered_markets.append(m)

    # 3. TRI PAR IMPORTANCE DE L'ANOMALIE
    # On classe les marchés du plus suspect au moins suspect
    filtered_markets = sorted(filtered_markets, key=lambda x: x['ratio'], reverse=True)

    if not filtered_markets:
        print("🔍 Aucun signal suspect détecté sur Polymarket pour le moment.")
        return []

    results = []

    # 4. ANALYSE PAR LE SWARM (Top 3 des anomalies)
    for market in filtered_markets[:3]:
        title = market['title']
        volume = market['volume']
        liquidity = market['liquidity']
        vol_liq_ratio = market['ratio']

        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es une équipe d'analystes spécialisés en Insider Trading. Ton but est de déterminer si un volume élevé cache une information privée ou du bruit."
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyse : '{title}'. 
                        Stats : Vol ${volume} | Liq ${liquidity} | Ratio : {vol_liq_ratio:.2f}.
                        Débats entre un expert Smart Money et un sceptique. Donne un verdict final sec."""
                    }
                ],
                model="llama-3.3-70b-specdec",
                temperature=0.2,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Score de confiance basé sur le ratio
            confidence_score = min(95, int(70 + (vol_liq_ratio * 2)))

            results.append(SwarmResult(
                thematique=title,
                final_verdict="ACHAT / ACCUMULATION" if vol_liq_ratio > 2 else "FLUX À SURVEILLER",
                confidence=confidence_score,
                summary=analysis_text,
                recommendation=f"Ratio élevé de {vol_liq_ratio:.2f}. Vérifier les news.",
                key_arguments=["Mouvement asymétrique Volume/Liquidité"],
                risk_assessment="ÉLEVÉ" if confidence_score > 85 else "MODÉRÉ",
                kelly_criterion=f"Miser {min(5, vol_liq_ratio):.1f}% du capital" if confidence_score > 80 else "Observer"
            ))
            
        except Exception as e:
            print(f"⚠️ Erreur d'analyse IA pour {title}: {e}")
            continue

    return results

# --- TEST LOCAL ---
if __name__ == "__main__":
    res_list = asyncio.run(test_swarm())
    for r in res_list:
        print(f"\n✅ SIGNAL DÉTECTÉ : {r.thematique}")
        print(f"Verdict : {r.final_verdict} (Confiance: {r.confidence}%)")