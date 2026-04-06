import requests
from datetime import datetime, timezone, timedelta

def get_trending_markets(limit=20, tag_filter=None):
    url = "https://gamma-api.polymarket.com/markets"
    params = {"limit": limit, "active": "true", "closed": "false"}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        markets = response.json()
        if not isinstance(markets, list):
            return []
        now = datetime.now(timezone.utc)
        min_date = now + timedelta(days=7)
        max_date = now + timedelta(days=90)
        filtered = []
        for m in markets:
            try:
                volume = float(m.get("volume", 0) or 0)
                end_date_str = m.get("endDate") or m.get("end_date") or ""
                if not end_date_str:
                    continue
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                if volume < 1000:
                    continue
                if end_date < min_date or end_date > max_date:
                    continue
                filtered.append(m)
            except:
                continue
        filtered.sort(key=lambda x: float(x.get("volume", 0) or 0), reverse=True)
        if tag_filter and filtered:
            keywords = {
                "crypto": ["bitcoin", "btc", "eth", "crypto", "solana", "coin"],
                "politics": ["election", "president", "trump", "vote", "congress", "senate"],
                "artificial-intelligence": ["ai", "gpt", "openai", "anthropic", "llm"],
                "sports": ["nhl", "nba", "nfl", "mlb", "stanley", "cup", "champion", "playoff"]
            }
            kws = keywords.get(tag_filter.lower(), [tag_filter.lower()])
            tag_filtered = [m for m in filtered if any(kw in (m.get("question", "") + m.get("slug", "")).lower() for kw in kws)]
            return tag_filtered[:12] if tag_filtered else filtered[:12]
        return filtered[:12]
    except Exception as e:
        print(f"Erreur get_trending_markets: {e}")
        return []
def get_top_holders(market_slug, limit=8, min_balance=500):
    try:
        url = "https://gamma-api.polymarket.com/markets"
        params = {"slug": market_slug}
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            market = data[0]
            condition_id = market.get("conditionId", "")
            if not condition_id:
                return []
            url2 = "https://data-api.polymarket.com/positions"
            params2 = {"conditionId": condition_id, "limit": limit}
            response2 = requests.get(url2, params=params2, timeout=15)
            response2.raise_for_status()
            holders = response2.json()
            if isinstance(holders, list):
                return [h for h in holders if float(h.get("size", 0)) >= min_balance]
        return []
    except Exception as e:
        print(f"Erreur get_top_holders: {e}")
        return []

def get_wallet_creation_time(wallet_address):
    return datetime.now(timezone.utc) - timedelta(days=45)

if __name__ == "__main__":
    print("Test api_client.py")
    markets = get_trending_markets(limit=20)
    print(f"{len(markets)} marches recuperes apres filtrage")
    for m in markets[:3]:
        print(f"  - {m.get('question', 'N/A')[:60]} | volume: {m.get('volume', 0)}")
