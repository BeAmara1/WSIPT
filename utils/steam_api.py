import requests
import pandas as pd

API_KEY = "C24C3EC946D011B8B432B9D4369541F6"


def get_owned_games(steam_id):
    url = (
        f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        f"?key={API_KEY}&steamid={steam_id}&include_appinfo=true"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        games = data.get("response", {}).get("games", [])

        if not games:
            return None

        df = pd.DataFrame(games)
        return df

    except Exception:
        return None


def get_user_profile(steam_id):
    url = (
        f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        f"?key={API_KEY}&steamids={steam_id}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        players = data.get("response", {}).get("players", [])

        if not players:
            return None

        return players[0]

    except Exception:
        return None


# =========================
# NOVA FUNÇÃO (COLE AQUI)
# =========================
def get_game_details(game_name):
    try:
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&l=portuguese&cc=BR"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()

        if not data["items"]:
            return None

        game = data["items"][0]
        appid = game["id"]

        details_url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=portuguese"
        details_response = requests.get(details_url)

        if details_response.status_code != 200:
            return None

        details_data = details_response.json()

        if not details_data[str(appid)]["success"]:
            return None

        info = details_data[str(appid)]["data"]

        return {
            "image": info.get("header_image"),
            "description": info.get("short_description")
        }

    except Exception:
        return None
    

    