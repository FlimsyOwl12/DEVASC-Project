"""Manual F6 live verification helper for the GraphHopper route application.

This script intentionally prints only inputs, status, and route summaries. It
loads the key from the project environment in the same way as the main app and
never displays the key or full request URL.
"""

import importlib.util
import os
from pathlib import Path
import sys

from dotenv import load_dotenv


APP_PATH = Path(__file__).with_name("graphhopper_parse-json_7.py")
SPEC = importlib.util.spec_from_file_location("graphhopper_app", APP_PATH)
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)

PROFILES_TO_CHECK = ("car", "bike", "foot")
REACHABLE_ROUTE = ("Manila City Hall, Manila", "Quezon Memorial Circle, Quezon City")
DISCONNECTED_ROUTE = ("Manila, Philippines", "Honolulu, Hawaii")


def geocode_checked(label, key):
    status, lat, lng, name = app.geocoding(label, key)
    if lat is None or lng is None:
        print(f"Geocoding failed for {label!r}; status={status}")
        return None
    return status, lat, lng, name


def verify_route(origin_label, destination_label, profile, key):
    print(f"\nProfile: {profile}")
    print(f"Input: {origin_label} -> {destination_label}")
    origin = geocode_checked(origin_label, key)
    destination = geocode_checked(destination_label, key)
    if origin is None or destination is None:
        print("Result: skipped routing after unsuccessful geocoding")
        return False
    route = app.routing(origin, destination, profile, key)
    if route is None:
        print("Result: no route returned")
        return False
    print(
        "Result: route returned; "
        f"distance={app.format_distance(route['distance'], 'metric')}; "
        f"duration_ms={int(route['time'])}; "
        f"steps={len(route['instructions'])}"
    )
    return True


def main():
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    key = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    if not key or key == "replace_with_your_own_key":
        print("Set GRAPHHOPPER_API_KEY before running live verification.")
        return 1

    print("GraphHopper live verification - no API keys are printed.")
    print(f"Reachable route: {REACHABLE_ROUTE[0]} -> {REACHABLE_ROUTE[1]}")
    supported = []
    unavailable = []
    for profile in PROFILES_TO_CHECK:
        if verify_route(REACHABLE_ROUTE[0], REACHABLE_ROUTE[1], profile, key):
            supported.append(profile)
        else:
            unavailable.append(profile)

    print("\nDisconnected-route behavior check")
    verify_route(DISCONNECTED_ROUTE[0], DISCONNECTED_ROUTE[1], "car", key)

    print("\nSummary")
    print("Supported/reachable profiles:", ", ".join(supported) or "none confirmed")
    print("Unavailable/failed profiles:", ", ".join(unavailable) or "none")
    return 0 if supported else 2


if __name__ == "__main__":
    sys.exit(main())
