import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

from chat import send_message

BASE_DIR = Path(__file__).resolve().parent
MATCHES_FILE = BASE_DIR / "matches.json"
KEYS_FILE = BASE_DIR / "keys.env"

load_dotenv(KEYS_FILE)

url = "https://api.football-data.org/v4/competitions/WC/matches"
match_filters = {"status": "FINISHED"}
api_key = os.getenv("API_KEY")
headers = {"X-Auth-Token": api_key}


def create_message(match: dict) -> str:
    home_name = match.get("homeTeam", {}).get("name", "Unknown")
    away_name = match.get("awayTeam", {}).get("name", "Unknown")
    home_score = match.get("score", {}).get("fullTime", {}).get("home", "?")
    away_score = match.get("score", {}).get("fullTime", {}).get("away", "?")
    message = f"⚽{home_name} ({home_score}) vs. {away_name} ({away_score})"
    print(f"Message created: {message}")
    return message

def get_message() -> str:
    return create_message(latest_match)

def main() -> None:
    response = requests.get(url, params=match_filters, headers=headers)
    response.raise_for_status()
    data = response.json()

    with MATCHES_FILE.open("r", encoding="utf-8") as f:
        existing_matches = json.load(f)

    latest_match = data.get("matches", [{}])[-1]
    print("Latest match from API:")
    

    if data != existing_matches:
        for match in data.get("matches", []):
            print(
                f"New match found: {match['homeTeam']['name']} vs {match['awayTeam']['name']} - Status: {match['status']}"
            )
        with MATCHES_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        send_message(create_message(latest_match))
    else:
        print("No new matches found.")


if __name__ == "__main__":
    main()