import os
import json
import requests

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
PLATFORM_ROUTING = "la1.api.riotgames.com"

TIER_ORDER = {
    "CHALLENGER": 9, "GRANDMASTER": 8, "MASTER": 7,
    "DIAMOND": 6, "EMERALD": 5, "PLATINUM": 4,
    "GOLD": 3, "SILVER": 2, "BRONZE": 1, "IRON": 0,
    "UNRANKED": -1
}
RANK_ORDER = {"I": 4, "II": 3, "III": 2, "IV": 1}

# Lista centralizada de participantes
PLAYERS = [
    {
        "name": "JuanTaicho",
        "tag": "SQCV1",
        "puuid": "TU_PUUID_AQUI",
        "category": "High Elo"
    },
    {
        "name": "Sebs",
        "tag": "SQCV2",
        "puuid": "PUUID_DE_SEBS",
        "category": "Mid Elo"
    },
    {
        "name": "Jacobobito",
        "tag": "SQCV3",
        "puuid": "PUUID_DE_JACOBOBITO",
        "category": "Low Elo"
    }
]

def fetch_soloq_data(puuid):
    url = f"https://{PLATFORM_ROUTING}/lol/league/v4/entries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            entries = res.json()
            for entry in entries:
                if entry.get("queueType") == "RANKED_SOLO_5x5":
                    return {
                        "tier": entry.get("tier", "UNRANKED"),
                        "rank": entry.get("rank", ""),
                        "leaguePoints": entry.get("leaguePoints", 0),
                        "wins": entry.get("wins", 0),
                        "losses": entry.get("losses", 0)
                    }
    except Exception as e:
        print(f"Error consultando PUUID {puuid}: {e}")

    return {
        "tier": "UNRANKED",
        "rank": "",
        "leaguePoints": 0,
        "wins": 0,
        "losses": 0
    }

def main():
    leaderboard = []
    
    for p in PLAYERS:
        stats = fetch_soloq_data(p["puuid"])
        
        # Cálculo de valor de ordenamiento
        tier_val = TIER_ORDER.get(stats["tier"], -1)
        rank_val = RANK_ORDER.get(stats["rank"], 0)
        score = (tier_val * 10000) + (rank_val * 1000) + stats["leaguePoints"]
        
        total_games = stats["wins"] + stats["losses"]
        winrate = round((stats["wins"] / total_games * 100), 1) if total_games > 0 else 0.0
        
        leaderboard.append({
            "name": p["name"],
            "tag": p["tag"],
            "category": p["category"],
            "tier": stats["tier"],
            "rank": stats["rank"],
            "lp": stats["leaguePoints"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "winrate": winrate,
            "score": score
        })
    
    # Ordenar ranking global
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    # Asignar posición global
    for idx, player in enumerate(leaderboard, start=1):
        player["position"] = idx

    output_dir = "public"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
