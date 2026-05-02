import requests

# =========================
# 🔧 CONFIGURAÇÃO STEAM API
# =========================
STEAM_API_KEY = "C24C3EC946D011B8B432B9D4369541F6"

BASE_URL = "https://api.steampowered.com"


# =========================
# 👤 PERFIL DO USUÁRIO
# =========================
def get_user_profile(steam_id):
    try:
        url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            "key": STEAM_API_KEY,
            "steamids": steam_id
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        players = data.get("response", {}).get("players", [])

        if not players:
            return None

        return players[0]

    except Exception as e:
        print("Erro get_user_profile:", e)
        return None


# =========================
# 🎮 JOGOS DA BIBLIOTECA
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

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        games = data.get("response", {}).get("games", [])

        if not games:
            return None

        return games

    except Exception as e:
        print("Erro get_owned_games:", e)
        return None


# =========================
# 🖼️ DETALHES DO JOGO
# =========================
def get_game_details(game_name):
    try:
        url = "https://store.steampowered.com/api/storesearch/"
        params = {
            "term": game_name,
            "l": "english",
            "cc": "us"
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        items = data.get("items", [])

        if not items:
            return None

        game = items[0]

        return {
            "image": game.get("tiny_image", ""),
            "name": game.get("name", ""),
            "id": game.get("id")
        }

    except Exception as e:
        print("Erro get_game_details:", e)
        return None