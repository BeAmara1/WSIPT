import requests

STEAM_API_KEY = "C24C3EC946D011B8B432B9D4369541F6"
BASE_URL = "https://api.steampowered.com"


# =========================
# 👤 PERFIL
# =========================
def get_user_profile(steam_id):
    try:
        url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            "key": STEAM_API_KEY,
            "steamids": steam_id
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        players = data.get("response", {}).get("players", [])
        return players[0] if players else None

    except Exception as e:
        print("get_user_profile error:", e)
        return None


# =========================
# 🎮 JOGOS
# =========================
def get_owned_games(steam_id):
    try:
        url = f"{BASE_URL}/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": STEAM_API_KEY,
            "steamid": steam_id,
            "include_appinfo": True,
            "include_played_free_games": True
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return data.get("response", {}).get("games", None)

    except Exception as e:
        print("get_owned_games error:", e)
        return None


# =========================
# 🖼️ DETALHES DO JOGO (VERSÃO SEGURA)
# =========================
def get_game_details(game_name):
    try:
        if not game_name:
            return None

        url = "https://store.steampowered.com/api/storesearch/"
        params = {
            "term": game_name,
            "l": "english",
            "cc": "us"
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        items = data.get("items", [])
        if not items:
            return None

        game = items[0]

        return {
            "image": game.get("tiny_image", ""),
            "name": game.get("name", ""),
            "id": game.get("id"),
            "description": game.get("name", "")
        }

    except Exception as e:
        print("get_game_details error:", e)
        return None