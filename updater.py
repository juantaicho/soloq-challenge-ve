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

# Lista centralizada de participantes (conserva tus PUUIDs reales aquí)
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
    },
    {
        "name": "JuanTaicho",
        "tag": "JUAN",
        "puuid": "PUUID_DE_JACOBOBITO",
        "category": "Low Elo"
    },
]

def get_summoner_id(puuid, headers):
    """Obtiene el summonerId a partir del puuid para consultar ligas de forma 100% compatible."""
    url = f"https://{PLATFORM_ROUTING}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json().get("id")
        else:
            print(f"[ERROR] No se pudo obtener SummonerID para {puuid} (Status {res.status_code}): {res.text}")
    except Exception as e:
        print(f"[EXCEPCIÓN] Obteniendo SummonerID: {e}")
    return None

def fetch_soloq_data(puuid):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    # 1. Intentar primero consultar por PUUID directamente
    url_puuid = f"https://{PLATFORM_ROUTING}/lol/league/v4/entries/by-puuid/{puuid}"
    entries = []
    
    try:
        res = requests.get(url_puuid, headers=headers, timeout=10)
        if res.status_code == 200:
            entries = res.json()
        elif res.status_code == 401 or res.status_code == 403:
            print("[ALERTA CRÍTICA] RIOT_API_KEY expirada o no autorizada (Status 401/403).")
            return fallback_stats()
    except Exception as e:
        print(f"[EXCEPCIÓN] Fallo de red consultando por PUUID: {e}")

    # 2. Si by-puuid vino vacío (muy común en LAN), consultar por summonerId
    if not entries:
        summoner_id = get_summoner_id(puuid, headers)
        if summoner_id:
            url_summoner = f"https://{PLATFORM_ROUTING}/lol/league/v4/entries/by-summoner/{summoner_id}"
            try:
                res_sum = requests.get(url_summoner, headers=headers, timeout=10)
                if res_sum.status_code == 200:
                    entries = res_sum.json()
                else:
                    print(f"[ERROR] Fallo al consultar por summonerId (Status {res_sum.status_code}): {res_sum.text}")
            except Exception as e:
                print(f"[EXCEPCIÓN] Fallo consultando por summonerId: {e}")

    # 3. Filtrar la cola RANKED_SOLO_5x5
    for entry in entries:
        if entry.get("queueType") == "RANKED_SOLO_5x5":
            return {
                "tier": entry.get("tier", "UNRANKED").upper(),
                "rank": entry.get("rank", ""),
                "leaguePoints": entry.get("leaguePoints", 0),
                "wins": entry.get("wins", 0),
                "losses": entry.get("losses", 0)
            }

    print(f"[INFO] No se encontraron entradas de Ranked SoloQ para PUUID: {puuid}. Entradas recibidas: {entries}")
    return fallback_stats()

def fallback_stats():
    return {
        "tier": "UNRANKED",
        "rank": "",
        "leaguePoints": 0,
        "wins": 0,
        "losses": 0
    }

def main():
    if not RIOT_API_KEY:
        print("[ERROR CRÍTICO] La variable RIOT_API_KEY no está configurada en los Secrets.")
        return

    leaderboard = []
    
    for p in PLAYERS:
        print(f"Consultando datos para {p['name']}...")
        stats = fetch_soloq_data(p["puuid"])
        
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
    
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    for idx, player in enumerate(leaderboard, start=1):
        player["position"] = idx

    output_dir = "public"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

    print("Actualización de leaderboard.json completada con éxito.")

if __name__ == "__main__":
    main()
