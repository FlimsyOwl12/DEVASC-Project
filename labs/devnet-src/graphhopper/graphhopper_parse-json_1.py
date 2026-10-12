"""Geocoding exercise adapted from Cocoasaur/devasc-graphhopper-api."""

import os
from pathlib import Path
import sys

import requests
from dotenv import load_dotenv


def main():
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    key = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    if not key or key == "replace_with_your_own_key":
        print("Set GRAPHHOPPER_API_KEY in the project's .env file or your environment.")
        return 1

    try:
        response = requests.get(
            "https://graphhopper.com/api/1/geocode",
            params={"q": "Washington, D.C.", "limit": 1, "key": key},
            timeout=15,
        )
        data = response.json()
    except requests.RequestException:
        print("The geocoding request failed. Check your connection and try again.")
        return 1
    except ValueError:
        print("The API did not return valid JSON.")
        return 1

    print("Geocoding API status:", response.status_code)
    print(str(data).replace(key, "[REDACTED]"))
    return 0 if response.status_code == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
