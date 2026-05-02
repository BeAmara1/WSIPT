print(">>> STEAM_API CARREGOU <<<")
print("FUNÇÕES:", dir())

import requests

STEAM_API_KEY = "C24C3EC946D011B8B432B9D4369541F6"
BASE_URL = "https://api.steampowered.com"


def get_user_profile(steam_id):
    try:
        r = requests.get(
            f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/",
            params={"key": STEAM_API_KEY, "steamids": steam_id},
            timeout=10
        )
        data = r.json()
        players = data.get("response", {}).get("players", [])
        return players[0] if players else None

    except Exception as e:
        print("profile error:", e)
        return None


def get_owned_games(steam_id):
    try:
        r = requests.get(
            f"{BASE_URL}/IPlayerService/GetOwnedGames/v1/",
            params={
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "include_appinfo": True,
                "include_played_free_games": True
            },
            timeout=10
        )

        data = r.json()
        return data.get("response", {}).get("games", None)

    except Exception as e:
        print("games error:", e)
        return None


def get_game_details(game_name):
    try:
        if not game_name:
            return None

        r = requests.get(
            "https://store.steampowered.com/api/storesearch/",
            params={
                "term": game_name,
                "l": "english",
                "cc": "us"
            },
            timeout=10
        )

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
        print("details error:", e)
        return None