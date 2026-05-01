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