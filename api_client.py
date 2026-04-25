import requests
from config import HEADERS

def get_trending_markets(limit=20, tag_filter=None, exclude_slugs=None):
    if exclude_slugs is None:
        exclude_slugs = []
        
    url = "https://gamma-api.polymarket.com/markets"
    params = {"limit": limit, "active": "true", "closed": "false"}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        markets = response.json()
        
        # Filtrage : Volume suffisant ET pas dans la liste des exclus
        filtered = [
            m for m in markets 
            if float(m.get("volume", 0) or 0) > 10 
            and m.get("slug") not in exclude_slugs
        ]
        
        if tag_filter:
            # On cherche le mot clé dans le titre ou les tags
            res = [m for m in filtered if tag_filter.lower() in m.get("question", "").lower()]
            # Si on ne trouve rien avec le mot clé, on prend les meilleurs du moment non-exclus
            return res[:5] if res else filtered[:5]
            
        return filtered[:5]
    except Exception as e:
        print(f"Erreur API Markets: {e}")
        return []

def get_top_holders(market_slug, limit=3):
    # Reste inchangé ou vide selon tes besoins
    return []