"""Lab baseline for DEVASC Option 1; enhancement tasks are in README.md.

Adapted from Cocoasaur/devasc-graphhopper-api at commit 2289d4d.
The lab provides routing; completed enhancements are tracked in README.md.
"""

import os
from pathlib import Path
import sys
import urllib.parse

import requests
from dotenv import load_dotenv


GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"
PROFILES = ("car", "bike", "foot")
TIMEOUT_SECONDS = 15


def geocoding(location, key):
    """Return the lab tuple (HTTP status, latitude, longitude, display name)."""
    url = GEOCODE_URL + urllib.parse.urlencode(
        {"q": location, "limit": 1, "key": key}
    )
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    data = response.json()
    if response.status_code != 200:
        message = str(data.get("message", "Geocoding failed.")).replace(key, "[REDACTED]")
        print(f"Geocoding API status: {response.status_code}\nError: {message}")
        return response.status_code, None, None, location
    if not data.get("hits"):
        print(f"No location found for: {location}")
        return response.status_code, None, None, location

    hit = data["hits"][0]
    name = ", ".join(
        part for part in (hit["name"], hit.get("state"), hit.get("country")) if part
    )
    print(f"Location: {name} (type: {hit.get('osm_value', 'location')})")
    return response.status_code, hit["point"]["lat"], hit["point"]["lng"], name


def routing(origin, destination, profile, key):
    """Use repeated GET point parameters in latitude,longitude order."""
    params = [
        ("key", key),
        ("profile", profile),
        ("point", f"{origin[1]},{origin[2]}"),
        ("point", f"{destination[1]},{destination[2]}"),
        ("instructions", "true"),
    ]
    url = ROUTE_URL + urllib.parse.urlencode(params)
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    data = response.json()
    print(f"Routing API status: {response.status_code}")
    if response.status_code != 200:
        message = str(data.get("message", "Could not calculate route.")).replace(key, "[REDACTED]")
        print(f"Error: {message}")
        return None
    if not data.get("paths"):
        print("No route was returned between these locations.")
        return None
    return data["paths"][0]


def format_distance(meters, units):
    """Convert an API distance in meters to the selected display unit."""
    if units == "metric":
        return f"{meters / 1000:.1f} km"
    if units == "imperial":
        return f"{meters / 1609.344:.1f} miles"
    raise ValueError("Choose metric or imperial units.")


def display_route(path, origin_name, destination_name, profile, units="metric"):
    """Keep the original plain-text summary as the team's starting point."""
    # TODO F2: improve the summary and numbered directions with a table/color.
    hours, remainder = divmod(int(path["time"] / 1000), 3600)
    minutes, seconds = divmod(remainder, 60)
    print("=" * 50)
    print(f"Directions from {origin_name} to {destination_name} by {profile}")
    print(f"Distance traveled: {format_distance(path['distance'], units)}")
    print(f"Trip duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
    print("=" * 50)
    for instruction in path["instructions"]:
        print(f"{instruction['text']} ({format_distance(instruction['distance'], units)})")
    print("=" * 50)


def read_input(prompt):
    """Allow q/quit even after a blank location is entered."""
    while True:
        value = input(prompt).strip()
        if value.lower() in ("q", "quit"):
            return None
        if value:
            return value
        print("Please enter a value, or q to quit.")


def read_units():
    """Ask again for unsupported units, and honor the usual quit keywords."""
    while True:
        units = read_input("Distance units (metric or imperial): ")
        if units is None:
            return None
        if units.lower() in ("metric", "imperial"):
            return units.lower()
        print("Please choose metric or imperial, or q to quit.")


def main():
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    key = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    if not key or key == "replace_with_your_own_key":
        print("Set GRAPHHOPPER_API_KEY in the project's .env file or your environment.")
        return 1

    print("DEVASC Option 1 — GraphHopper lab baseline. Enter q or quit to exit.")
    while True:
        try:
            profile = read_input("Travel profile (car, bike, foot): ")
            if profile is None:
                break
            profile = profile.lower()
            if profile not in PROFILES:
                profile = "car"
                print("Unknown profile. Using car.")
            units = read_units()
            if units is None:
                break
            location = read_input("Starting location: ")
            if location is None:
                break
            origin = geocoding(location, key)
            if origin[1] is None or origin[2] is None:
                continue
            location = read_input("Destination: ")
            if location is None:
                break
            destination = geocoding(location, key)
            if destination[1] is None or destination[2] is None:
                continue
            path = routing(origin, destination, profile, key)
            if path is not None:
                display_route(path, origin[3], destination[3], profile, units)
        except requests.RequestException:
            print("The request failed or timed out. Check your connection and try again.")
        except ValueError:
            print("The API response could not be read. Please try again.")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
