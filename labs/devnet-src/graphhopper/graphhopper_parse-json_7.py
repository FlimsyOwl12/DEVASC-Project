"""Lab baseline for DEVASC Option 1; enhancement tasks are in README.md.

Adapted from Cocoasaur/devasc-graphhopper-api at commit 2289d4d.
The lab provides routing; completed enhancements are tracked in README.md.
"""

import math
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


class APIResponseError(ValueError):
    """An API reply cannot safely be used by the directions application."""


def redact(text, key):
    return text.replace(key, "[REDACTED]") if key else text


def json_object(response, service):
    try:
        data = response.json()
    except ValueError:
        raise APIResponseError(f"{service} returned invalid JSON.") from None
    if not isinstance(data, dict):
        raise APIResponseError(f"{service} returned an unexpected JSON format.")
    return data


def api_message(data, key, fallback):
    message = data.get("message")
    return redact(message, key) if isinstance(message, str) and message.strip() else fallback


def number(value, label, minimum, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise APIResponseError(f"{label} must be a number.")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or value < minimum or (maximum is not None and value > maximum):
        raise APIResponseError(f"{label} is outside the supported range.")
    return value


def validate_path(path, key):
    if not isinstance(path, dict):
        raise APIResponseError("Routing returned an invalid path.")
    distance = number(path.get("distance"), "Routing distance", 0)
    duration = number(path.get("time"), "Routing duration", 0)
    steps = path.get("instructions")
    if not isinstance(steps, list):
        raise APIResponseError("Routing did not return a valid instruction list.")
    instructions = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise APIResponseError(f"Routing instruction {index} is invalid.")
        text = step.get("text")
        if not isinstance(text, str) or not text.strip():
            raise APIResponseError(f"Routing instruction {index} has no valid text.")
        step_distance = number(step.get("distance"), f"Instruction {index} distance", 0)
        instructions.append({**step, "text": redact(text, key), "distance": step_distance})
    return {**path, "distance": distance, "time": duration, "instructions": instructions}


def geocoding(location, key):
    """Return the lab tuple (HTTP status, latitude, longitude, display name)."""
    url = GEOCODE_URL + urllib.parse.urlencode(
        {"q": location, "limit": 1, "key": key}
    )
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    data = json_object(response, "Geocoding")
    if response.status_code != 200:
        message = api_message(data, key, "Geocoding failed.")
        print(f"Geocoding API status: {response.status_code}\nError: {message}")
        return response.status_code, None, None, location
    hits = data.get("hits")
    if not isinstance(hits, list):
        raise APIResponseError("Geocoding did not return a valid hits list.")
    if not hits:
        print(f"No location found for: {redact(location, key)}")
        return response.status_code, None, None, location

    hit = hits[0]
    if not isinstance(hit, dict) or not isinstance(hit.get("point"), dict):
        raise APIResponseError("Geocoding returned invalid coordinates.")
    latitude = number(hit["point"].get("lat"), "Latitude", -90, 90)
    longitude = number(hit["point"].get("lng"), "Longitude", -180, 180)
    if not isinstance(hit.get("name"), str) or not hit["name"].strip():
        raise APIResponseError("Geocoding did not return a valid place name.")
    for field in ("state", "country"):
        if hit.get(field) is not None and not isinstance(hit[field], str):
            raise APIResponseError(f"Geocoding returned an invalid {field} name.")
    name = ", ".join(
        redact(part.strip(), key)
        for part in (hit["name"], hit.get("state"), hit.get("country"))
        if part and part.strip()
    )
    location_type = hit.get("osm_value")
    if not isinstance(location_type, str):
        location_type = "location"
    print(f"Location: {name} (type: {redact(location_type, key)})")
    return response.status_code, latitude, longitude, name


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
    data = json_object(response, "Routing")
    print(f"Routing API status: {response.status_code}")
    if response.status_code != 200:
        message = api_message(data, key, "Could not calculate route.")
        print(f"Error: {message}")
        return None
    paths = data.get("paths")
    if not isinstance(paths, list):
        raise APIResponseError("Routing did not return a valid paths list.")
    if not paths:
        print("No route was returned between these locations.")
        return None
    return validate_path(paths[0], key)


def format_distance(meters, units):
    """Convert an API distance in meters to the selected display unit."""
    if units == "metric":
        return f"{meters / 1000:.1f} km"
    if units == "imperial":
        return f"{meters / 1609.344:.1f} miles"
    raise ValueError("Choose metric or imperial units.")


def display_route(path, origin_name, destination_name, profile, units="metric", output_mode="detailed"):
    """Print the route summary, optionally followed by numbered directions."""
    if output_mode not in ("summary", "detailed"):
        raise ValueError("Choose summary or detailed output.")
    hours, remainder = divmod(int(path["time"] / 1000), 3600)
    minutes, seconds = divmod(remainder, 60)
    rows = [
        ("Origin", origin_name),
        ("Destination", destination_name),
        ("Profile", profile),
        ("Units", units.capitalize()),
        ("Distance", format_distance(path["distance"], units)),
        ("Duration", f"{hours:02d}:{minutes:02d}:{seconds:02d}"),
    ]
    width = max(len(label) for label, _ in rows)
    print("ROUTE SUMMARY")
    print("=" * 50)
    for label, value in rows:
        print(f"{label:<{width}} : {value}")
    if output_mode == "detailed":
        print("\nDIRECTIONS")
        for number, instruction in enumerate(path["instructions"], start=1):
            print(f"{number:>2}. {instruction['text']} ({format_distance(instruction['distance'], units)})")
        if not path["instructions"]:
            print("No direction steps returned.")
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


def read_output_mode():
    """Choose a route view before making any API requests."""
    while True:
        mode = read_input("Output mode (summary or detailed): ")
        if mode is None:
            return None
        if mode.lower() in ("summary", "detailed"):
            return mode.lower()
        print("Please choose summary or detailed, or q to quit.")


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
            output_mode = read_output_mode()
            if output_mode is None:
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
                display_route(path, origin[3], destination[3], profile, units, output_mode)
        except APIResponseError as error:
            print(f"API response error: {error} Please try again.")
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
