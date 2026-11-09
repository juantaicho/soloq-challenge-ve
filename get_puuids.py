import os
import requests

# Lee la clave desde la variable de entorno del sistema de forma segura[cite: 1]
RIOT_API_KEY = os.getenv("RIOT_API_KEY")[cite: 1]

if not RIOT_API_KEY:
    raise ValueError(
        "No se encontró la variable RIOT_API_KEY en el entorno.\n"
        "Configúrala en tu terminal antes de ejecutar el script:\n"
        "  En PowerShell: $env:RIOT_API_KEY=\"RGAPI-tu-llave-aqui\"\n"
        "  En CMD:        set RIOT_API_KEY=RGAPI-tu-llave-aqui"
    )[cite: 1]

# Para cuentas en servidores de LAN, LAS y NA, el ruteo continental de cuentas es 'americas'[cite: 1]
ROUTING_REGION = "americas.api.riotgames.com"[cite: 1]

# Lista de jugadores a consultar: (gameName, tagLine, categoría)[cite: 1]
PARTICIPANTES = [
    ("JuanTaicho", "JUAN", "High Elo"),
    ("Sebs", "SQCV2", "Mid Elo"),
    ("Jacobobito", "SQCV3", "Low Elo"),
    # Agrega aquí a los siguientes participantes conforme confirmen:
    # ("InvocadorEjemplo", "SQCV4", "Mid Elo"),
][cite: 1]

def obtener_puuids():
    headers = {"X-Riot-Token": RIOT_API_KEY}[cite: 1]
    jugadores_listos = [][cite: 1]

    print("Consultando PUUIDs a Riot Games...\n")[cite: 1]

    for game_name, tag_line, category in PARTICIPANTES:[cite: 1]
        url = f"https://{ROUTING_REGION}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"[cite: 1]
        try:
            res = requests.get(url, headers=headers, timeout=10)[cite: 1]
            if res.status_code == 200:[cite: 1]
                data = res.json()[cite: 1]
                puuid = data.get("puuid")[cite: 1]
                jugadores_listos.append({
                    "name": game_name,
                    "tag": tag_line,
                    "puuid": puuid,
                    "category": category
                })[cite: 1]
                print(f"✓ {game_name}#{tag_line} -> {puuid}")[cite: 1]
            elif res.status_code == 404:[cite: 1]
                print(f"✗ Error 404: No se encontró la cuenta {game_name}#{tag_line}. Verifica el Riot ID.")[cite: 1]
            elif res.status_code in [401, 403]:[cite: 1]
                print("✗ Error de autenticación: Tu RIOT_API_KEY es inválida o ha expirado.")[cite: 1]
                break
            else:
                print(f"✗ Error {res.status_code} al consultar {game_name}#{tag_line}: {res.text}")[cite: 1]
        except Exception as e:[cite: 1]
            print(f"✗ Error de conexión con {game_name}#{tag_line}: {e}")[cite: 1]

    print("\n--- COPIA Y PEGA ESTO DIRECTAMENTE EN TU updater.py ---\n")[cite: 1]
    print("PLAYERS = [")[cite: 1]
    for j in jugadores_listos:[cite: 1]
        print(f"    {{\n        \"name\": \"{j['name']}\",\n        \"tag\": \"{j['tag']}\",\n        \"puuid\": \"{j['puuid']}\",\n        \"category\": \"{j['category']}\"\n    }},")[cite: 1]
    print("]")[cite: 1]

if __name__ == "__main__":
    obtener_puuids()[cite: 1]
