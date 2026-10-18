"""Lab baseline for DEVASC Option 1; enhancement tasks are in README.md.

Adapted from Cocoasaur/devasc-graphhopper-api at commit 2289d4d.
The lab provides routing; completed enhancements are tracked in README.md.
"""

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.parse

import requests
from dotenv import load_dotenv


GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"
PROFILES = ("car", "bike", "foot")
TIMEOUT_SECONDS = 15
DEFAULT_GEOCODE_LIMIT = 5
MAX_HISTORY_SIZE = 10
EXPORTS_DIR = Path(__file__).resolve().parents[3] / "exports"

WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


class APIResponseError(ValueError):
    """An API reply cannot safely be used by the directions application."""


def current_timestamp():
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def convert_distance(meters, units):
    """Convert raw distance in meters to (value, unit_label) for the selected unit."""
    if units == "metric":
        return meters / 1000.0, "km"
    if units == "imperial":
        return meters / 1609.344, "miles"
    raise ValueError("Choose metric or imperial units.")


def format_distance(meters, units):
    """Convert an API distance in meters to the selected display unit."""
    value, unit_label = convert_distance(meters, units)
    return f"{value:.1f} {unit_label}"


def format_duration(duration_ms):
    """Format a duration in milliseconds as HH:MM:SS."""
    hours, remainder = divmod(int(duration_ms / 1000), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def duration_in_minutes(duration_ms):
    """Convert a duration in milliseconds to rounded minutes."""
    return round(duration_ms / 60000.0, 2)


@dataclass
class RouteRecord:
    """Internal representation of a validated route without API credentials."""

    origin: str
    destination: str
    origin_coords: tuple[float, float]
    destination_coords: tuple[float, float]
    profile: str
    units: str
    distance_meters: float
    duration_ms: float
    instructions: list[dict] = field(default_factory=list)
    timestamp: str = field(default_factory=current_timestamp)

    @property
    def distance_value(self) -> float:
        value, _ = convert_distance(self.distance_meters, self.units)
        return round(value, 2)

    @property
    def distance_unit(self) -> str:
        _, unit_label = convert_distance(self.distance_meters, self.units)
        return unit_label

    @property
    def formatted_distance(self) -> str:
        return format_distance(self.distance_meters, self.units)

    @property
    def duration_minutes(self) -> float:
        return duration_in_minutes(self.duration_ms)

    @property
    def formatted_duration(self) -> str:
        return format_duration(self.duration_ms)

    def to_path_dict(self) -> dict:
        return {
            "distance": self.distance_meters,
            "time": self.duration_ms,
            "instructions": [
                {"text": step["text"], "distance": step["distance"]}
                for step in self.instructions
            ],
        }


class RouteHistory:
    """Session-based storage for the most recent successfully generated routes."""

    def __init__(self, max_size: int = MAX_HISTORY_SIZE):
        if isinstance(max_size, bool) or not isinstance(max_size, int) or max_size < 1:
            raise ValueError("max_size must be a positive integer.")
        self.max_size = max_size
        self._records: list[RouteRecord] = []

    def add(self, record: RouteRecord) -> None:
        if not isinstance(record, RouteRecord):
            raise TypeError("Only RouteRecord instances can be stored in route history.")
        self._records.append(record)
        if len(self._records) > self.max_size:
            self._records = self._records[-self.max_size:]

    def entries(self) -> list[RouteRecord]:
        return list(self._records)

    def get(self, index: int) -> RouteRecord:
        if isinstance(index, bool) or not isinstance(index, int) or index < 1 or index > len(self._records):
            raise IndexError("Route history selection is out of range.")
        return self._records[index - 1]

    def clear(self) -> None:
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)

    def __bool__(self) -> bool:
        return bool(self._records)


def create_route_record(path, origin, destination, profile="car", units="metric", timestamp=None, key=None):
    """Build a consistent RouteRecord from validated geocoding and routing results."""
    if isinstance(path, RouteRecord):
        return path
    if units not in ("metric", "imperial"):
        raise ValueError("Choose metric or imperial units.")
    if isinstance(origin, (tuple, list)) and len(origin) >= 4:
        origin_coords = (float(origin[1]), float(origin[2]))
        origin_name = str(origin[3])
    else:
        origin_coords = (0.0, 0.0)
        origin_name = str(origin)

    if isinstance(destination, (tuple, list)) and len(destination) >= 4:
        dest_coords = (float(destination[1]), float(destination[2]))
        dest_name = str(destination[3])
    else:
        dest_coords = (0.0, 0.0)
        dest_name = str(destination)

    distance_meters = number(path.get("distance"), "Routing distance", 0)
    duration_ms = number(path.get("time"), "Routing duration", 0)
    raw_steps = path.get("instructions", [])
    if not isinstance(raw_steps, list):
        raise APIResponseError("Routing did not return a valid instruction list.")

    clean_steps = []
    for index, step in enumerate(raw_steps, start=1):
        if not isinstance(step, dict):
            raise APIResponseError(f"Routing instruction {index} is invalid.")
        text = step.get("text")
        if not isinstance(text, str) or not text.strip():
            raise APIResponseError(f"Routing instruction {index} has no valid text.")
        step_dist = number(step.get("distance"), f"Instruction {index} distance", 0)
        clean_steps.append({
            "text": redact(text.strip(), key),
            "distance": step_dist,
        })

    return RouteRecord(
        origin=redact(origin_name, key),
        destination=redact(dest_name, key),
        origin_coords=origin_coords,
        destination_coords=dest_coords,
        profile=redact(str(profile), key),
        units=units,
        distance_meters=distance_meters,
        duration_ms=duration_ms,
        instructions=clean_steps,
        timestamp=timestamp or current_timestamp(),
    )


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


def parse_geocode_candidate(hit, key):
    """Validate a single geocoding hit and extract its coordinates and display label."""
    if not isinstance(hit, dict) or not isinstance(hit.get("point"), dict):
        raise APIResponseError("Geocoding returned invalid coordinates.")
    latitude = number(hit["point"].get("lat"), "Latitude", -90, 90)
    longitude = number(hit["point"].get("lng"), "Longitude", -180, 180)
    if not isinstance(hit.get("name"), str) or not hit["name"].strip():
        raise APIResponseError("Geocoding did not return a valid place name.")
    for field in ("city", "state", "country"):
        if hit.get(field) is not None and not isinstance(hit[field], str):
            raise APIResponseError(f"Geocoding returned an invalid {field} name.")
    parts = []
    for raw_part in (hit["name"], hit.get("city"), hit.get("state"), hit.get("country")):
        if raw_part and raw_part.strip():
            cleaned = redact(raw_part.strip(), key)
            if not parts or cleaned.lower() != parts[-1].lower():
                parts.append(cleaned)
    name = ", ".join(parts)
    location_type = hit.get("osm_value")
    if not isinstance(location_type, str) or not location_type.strip():
        location_type = "location"
    return {
        "lat": latitude,
        "lng": longitude,
        "name": name,
        "type": redact(location_type.strip(), key),
    }


def extract_geocode_candidates(hits, key, max_candidates=DEFAULT_GEOCODE_LIMIT):
    """Filter valid geocoding candidates up to max_candidates, rejecting malformed hits."""
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or max_candidates < 1:
        raise ValueError("max_candidates must be a positive integer.")
    candidates = []
    first_error = None
    for hit in hits:
        try:
            candidate = parse_geocode_candidate(hit, key)
            candidates.append(candidate)
            if len(candidates) >= max_candidates:
                break
        except APIResponseError as error:
            if first_error is None:
                first_error = error
    if not candidates and first_error is not None:
        raise first_error
    return candidates


def prompt_candidate_selection(query, candidates, key=None):
    """Display numbered geocoding candidates and return the selected candidate, 'RETRY', or 'QUIT'."""
    safe_query = redact(query, key)
    print(f'\nSearch results for "{safe_query}":\n')
    for idx, candidate in enumerate(candidates, start=1):
        print(
            f"{idx}. {candidate['name']} "
            f"(lat: {candidate['lat']}, lng: {candidate['lng']})"
        )
    print()
    prompt_text = f"Select a location (1-{len(candidates)}), R to search again, or Q to quit: "
    while True:
        choice = input(prompt_text).strip()
        lower = choice.lower()
        if lower in ("q", "quit"):
            return "QUIT"
        if lower in ("r", "retry", "search"):
            return "RETRY"
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(candidates):
                return candidates[index - 1]
        print(
            f"Invalid selection. Please enter a number from 1 to {len(candidates)}, "
            "R to search again, or Q to quit."
        )


def geocoding(location, key, limit=DEFAULT_GEOCODE_LIMIT):
    """Return the lab tuple (HTTP status, latitude, longitude, display name).

    When multiple valid candidates are returned, prompts the user to choose the
    intended candidate, search again (R), or quit (Q). If the user quits during
    selection, returns (None, None, None, current_location).
    """
    current_location = location
    while True:
        url = GEOCODE_URL + urllib.parse.urlencode(
            {"q": current_location, "limit": limit, "key": key}
        )
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        data = json_object(response, "Geocoding")
        if response.status_code != 200:
            message = api_message(data, key, "Geocoding failed.")
            print(f"Geocoding API status: {response.status_code}\nError: {message}")
            return response.status_code, None, None, current_location
        hits = data.get("hits")
        if not isinstance(hits, list):
            raise APIResponseError("Geocoding did not return a valid hits list.")
        if not hits:
            print(f"No location found for: {redact(current_location, key)}")
            return response.status_code, None, None, current_location

        candidates = extract_geocode_candidates(hits, key, max_candidates=limit)
        if len(candidates) == 1:
            chosen = candidates[0]
            print(f"Location: {chosen['name']} (type: {chosen['type']})")
            return response.status_code, chosen["lat"], chosen["lng"], chosen["name"]

        selected = prompt_candidate_selection(current_location, candidates, key)
        if selected == "QUIT":
            return None, None, None, current_location
        if selected == "RETRY":
            new_location = read_input("Enter location to search: ")
            if new_location is None:
                return None, None, None, current_location
            current_location = new_location
            continue
        print(f"Location: {selected['name']} (type: {selected['type']})")
        return response.status_code, selected["lat"], selected["lng"], selected["name"]


def routing(origin, destination, profile, key):
    """Use repeated GET point parameters in latitude,longitude order."""
    if (
        not isinstance(origin, (tuple, list))
        or len(origin) < 3
        or origin[1] is None
        or origin[2] is None
        or not isinstance(destination, (tuple, list))
        or len(destination) < 3
        or destination[1] is None
        or destination[2] is None
    ):
        raise ValueError("Routing requires valid origin and destination coordinates.")
    origin_lat = number(origin[1], "Origin latitude", -90, 90)
    origin_lng = number(origin[2], "Origin longitude", -180, 180)
    dest_lat = number(destination[1], "Destination latitude", -90, 90)
    dest_lng = number(destination[2], "Destination longitude", -180, 180)
    params = [
        ("key", key),
        ("profile", profile),
        ("point", f"{origin_lat},{origin_lng}"),
        ("point", f"{dest_lat},{dest_lng}"),
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


def display_route(path, origin_name=None, destination_name=None, profile="car", units="metric", output_mode="detailed"):
    """Print the route summary, optionally followed by numbered directions."""
    if isinstance(path, RouteRecord):
        record = path
        if origin_name is not None:
            record = create_route_record(
                record.to_path_dict(),
                origin_name,
                destination_name if destination_name is not None else record.destination,
                profile,
                units,
                timestamp=record.timestamp,
            )
    else:
        record = create_route_record(path, origin_name or "", destination_name or "", profile, units)

    if output_mode not in ("summary", "detailed"):
        raise ValueError("Choose summary or detailed output.")
    rows = [
        ("Origin", record.origin),
        ("Destination", record.destination),
        ("Profile", record.profile),
        ("Units", record.units.capitalize()),
        ("Distance", record.formatted_distance),
        ("Duration", record.formatted_duration),
    ]
    width = max(len(label) for label, _ in rows)
    print("ROUTE SUMMARY")
    print("=" * 50)
    for label, value in rows:
        print(f"{label:<{width}} : {value}")
    if output_mode == "detailed":
        print("\nDIRECTIONS")
        for step_number, instruction in enumerate(record.instructions, start=1):
            print(
                f"{step_number:>2}. {instruction['text']} "
                f"({format_distance(instruction['distance'], record.units)})"
            )
        if not record.instructions:
            print("No direction steps returned.")
    print("=" * 50)


def sanitize_filename_component(text, max_length=30):
    """Sanitize a user or location string into a safe filename component."""
    if not isinstance(text, str):
        return "location"
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().lower()).strip("_")
    cleaned = cleaned[:max_length].strip("_")
    if not cleaned or cleaned in WINDOWS_RESERVED_NAMES:
        return "location"
    return cleaned


def build_export_filename(record, fmt):
    """Create a default safe filename from origin, destination, timestamp, and format."""
    fmt_clean = str(fmt).strip().lower().lstrip(".")
    if fmt_clean not in ("txt", "json", "csv"):
        raise ValueError("Unsupported export format. Choose txt, json, or csv.")
    origin_slug = sanitize_filename_component(record.origin)
    dest_slug = sanitize_filename_component(record.destination)
    ts_digits = re.sub(r"[^0-9]", "", str(record.timestamp))[:14]
    if not ts_digits:
        ts_digits = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"route_{origin_slug}_to_{dest_slug}_{ts_digits}.{fmt_clean}"


def validate_safe_filename(filename, expected_ext):
    """Validate a user-provided filename and prevent path traversal."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Filename cannot be empty.")
    raw = filename.strip()
    if "\x00" in raw or "/" in raw or "\\" in raw or ":" in raw or ".." in raw:
        raise ValueError("Invalid filename: path separators and traversal sequences are not allowed.")
    candidate = Path(raw)
    if candidate.is_absolute() or len(candidate.parts) != 1 or candidate.name in (".", ".."):
        raise ValueError("Invalid filename.")
    ext = str(expected_ext).strip().lower().lstrip(".")
    if ext not in ("txt", "json", "csv"):
        raise ValueError("Unsupported export format. Choose txt, json, or csv.")
    stem = candidate.stem if candidate.suffix.lower() == f".{ext}" else candidate.name
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    if not safe_stem or safe_stem.lower() in WINDOWS_RESERVED_NAMES or ".." in safe_stem:
        raise ValueError("Filename does not contain a valid name.")
    return f"{safe_stem}.{ext}"


def resolve_export_target(export_dir, safe_filename):
    """Resolve the target file path and guarantee it remains inside export_dir."""
    if export_dir is None or (isinstance(export_dir, str) and not export_dir.strip()):
        raise ValueError("Export directory cannot be empty.")
    export_root = Path(export_dir).resolve()
    target = (export_root / safe_filename).resolve()
    if target.parent != export_root:
        raise ValueError("Invalid export path: target must remain inside the exports directory.")
    return export_root, target


def unique_export_path(target_path):
    """Return a non-existing path by appending _1, _2, etc. when target_path exists."""
    target = Path(target_path)
    if not target.exists():
        return target
    parent = target.parent
    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def format_route_txt(record, exported_at=None, key=None):
    """Render a human-readable TXT export string for a route."""
    timestamp = redact(exported_at or record.timestamp or current_timestamp(), key)
    rows = [
        ("Origin", redact(record.origin, key)),
        ("Destination", redact(record.destination, key)),
        ("Profile", redact(record.profile, key)),
        ("Units", record.units.capitalize()),
        ("Distance", record.formatted_distance),
        ("Duration", record.formatted_duration),
        ("Exported At", timestamp),
    ]
    width = max(len(label) for label, _ in rows)
    lines = [
        "ROUTE EXPORT",
        "=" * 50,
    ]
    for label, value in rows:
        lines.append(f"{label:<{width}} : {value}")
    lines.append("")
    lines.append("DIRECTIONS")
    if record.instructions:
        for step_num, step in enumerate(record.instructions, start=1):
            step_text = redact(step["text"], key)
            step_dist = format_distance(step["distance"], record.units)
            lines.append(f"{step_num:>2}. {step_text} ({step_dist})")
    else:
        lines.append("No direction steps returned.")
    lines.append("=" * 50)
    return "\n".join(lines) + "\n"


def build_route_json_payload(record, exported_at=None, key=None):
    """Build the structured dictionary for JSON export."""
    timestamp = redact(exported_at or record.timestamp or current_timestamp(), key)
    dist_val, dist_unit = convert_distance(record.distance_meters, record.units)
    instructions_out = []
    for step_num, step in enumerate(record.instructions, start=1):
        step_val, step_unit = convert_distance(step["distance"], record.units)
        instructions_out.append({
            "step": step_num,
            "text": redact(step["text"], key),
            "distance": {
                "value": round(step_val, 2),
                "unit": step_unit,
                "formatted": format_distance(step["distance"], record.units),
            },
        })
    return {
        "origin": redact(record.origin, key),
        "destination": redact(record.destination, key),
        "profile": redact(record.profile, key),
        "units": record.units,
        "distance": {
            "value": round(dist_val, 2),
            "unit": dist_unit,
            "formatted": record.formatted_distance,
        },
        "duration": {
            "value": record.duration_minutes,
            "unit": "minutes",
            "formatted": record.formatted_duration,
        },
        "instructions": instructions_out,
        "exported_at": timestamp,
    }


def format_route_json(record, exported_at=None, key=None):
    """Serialize a route to a formatted JSON string."""
    payload = build_route_json_payload(record, exported_at=exported_at, key=key)
    return json.dumps(payload, indent=2) + "\n"


CSV_COLUMNS = (
    "origin",
    "destination",
    "profile",
    "units",
    "total_distance",
    "distance_unit",
    "duration_minutes",
    "duration_formatted",
    "step_number",
    "instruction",
    "step_distance",
    "step_distance_formatted",
    "exported_at",
)


def build_route_csv_rows(record, exported_at=None, key=None):
    """Build tabular CSV rows containing route metadata and turn-by-turn directions."""
    timestamp = redact(exported_at or record.timestamp or current_timestamp(), key)
    total_val, dist_unit = convert_distance(record.distance_meters, record.units)
    base = {
        "origin": redact(record.origin, key),
        "destination": redact(record.destination, key),
        "profile": redact(record.profile, key),
        "units": record.units,
        "total_distance": f"{total_val:.1f}",
        "distance_unit": dist_unit,
        "duration_minutes": f"{record.duration_minutes:.2f}",
        "duration_formatted": record.formatted_duration,
        "exported_at": timestamp,
    }
    rows = []
    if record.instructions:
        for step_num, step in enumerate(record.instructions, start=1):
            step_val, _ = convert_distance(step["distance"], record.units)
            rows.append({
                **base,
                "step_number": step_num,
                "instruction": redact(step["text"], key),
                "step_distance": f"{step_val:.1f}",
                "step_distance_formatted": format_distance(step["distance"], record.units),
            })
    else:
        rows.append({
            **base,
            "step_number": 0,
            "instruction": "No direction steps returned.",
            "step_distance": "0.0",
            "step_distance_formatted": format_distance(0, record.units),
        })
    return rows


def export_route(
    record,
    fmt,
    export_dir=EXPORTS_DIR,
    filename=None,
    overwrite=False,
    auto_rename=False,
    key=None,
):
    """Export a RouteRecord to TXT, JSON, or CSV inside export_dir and return the saved Path."""
    if not isinstance(record, RouteRecord):
        raise TypeError("export_route requires a RouteRecord instance.")
    fmt_clean = str(fmt).strip().lower().lstrip(".")
    if fmt_clean not in ("txt", "json", "csv"):
        raise ValueError("Unsupported export format. Choose txt, json, or csv.")

    safe_name = (
        validate_safe_filename(filename, fmt_clean)
        if filename is not None
        else build_export_filename(record, fmt_clean)
    )
    export_root, target = resolve_export_target(export_dir, safe_name)
    export_root.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        if auto_rename:
            target = unique_export_path(target)
        else:
            raise FileExistsError(f"Export file already exists: {target.name}")

    write_mode = "w" if overwrite else "x"
    exported_at = record.timestamp or current_timestamp()
    if fmt_clean == "txt":
        content = format_route_txt(record, exported_at=exported_at, key=key)
        with target.open(write_mode, encoding="utf-8") as handle:
            handle.write(content)
    elif fmt_clean == "json":
        content = format_route_json(record, exported_at=exported_at, key=key)
        with target.open(write_mode, encoding="utf-8") as handle:
            handle.write(content)
    elif fmt_clean == "csv":
        rows = build_route_csv_rows(record, exported_at=exported_at, key=key)
        with target.open(write_mode, encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    return target


def export_route_txt(record, export_dir=EXPORTS_DIR, filename=None, overwrite=False, auto_rename=False, key=None):
    """Export a route to a human-readable TXT file."""
    return export_route(
        record, "txt", export_dir=export_dir, filename=filename, overwrite=overwrite, auto_rename=auto_rename, key=key
    )


def export_route_json(record, export_dir=EXPORTS_DIR, filename=None, overwrite=False, auto_rename=False, key=None):
    """Export a route to a structured JSON file."""
    return export_route(
        record, "json", export_dir=export_dir, filename=filename, overwrite=overwrite, auto_rename=auto_rename, key=key
    )


def export_route_csv(record, export_dir=EXPORTS_DIR, filename=None, overwrite=False, auto_rename=False, key=None):
    """Export a route to a tabular CSV file using Python's built-in csv module."""
    return export_route(
        record, "csv", export_dir=export_dir, filename=filename, overwrite=overwrite, auto_rename=auto_rename, key=key
    )


def prompt_export_format_and_save(record, export_dir=EXPORTS_DIR, key=None):
    """Prompt the user for an export format (TXT, JSON, CSV, or Cancel) and save the route."""
    print("\nSelect export format:")
    print("1. TXT")
    print("2. JSON")
    print("3. CSV")
    print("4. Cancel")
    format_map = {
        "1": "txt",
        "txt": "txt",
        "2": "json",
        "json": "json",
        "3": "csv",
        "csv": "csv",
    }
    while True:
        choice = input("Select an option (1-4): ").strip().lower()
        if choice in ("4", "cancel", "c", "q", "quit"):
            print("Export cancelled.")
            return None
        if choice in format_map:
            fmt = format_map[choice]
            break
        print("Invalid export option. Please choose 1 (TXT), 2 (JSON), 3 (CSV), or 4 (Cancel).")

    filename = None
    auto_rename = False
    while True:
        try:
            saved_path = export_route(
                record,
                fmt,
                export_dir=export_dir,
                filename=filename,
                overwrite=False,
                auto_rename=auto_rename,
                key=key,
            )
            print(f"Route exported successfully to: {redact(str(saved_path), key)}")
            return saved_path
        except FileExistsError:
            attempted = filename or build_export_filename(record, fmt)
            print(f"File '{attempted}' already exists.")
            replacement = input(
                "Enter a different filename, press Enter to auto-rename, or C to cancel: "
            ).strip()
            if replacement.lower() in ("c", "cancel", "q", "quit"):
                print("Export cancelled.")
                return None
            if not replacement:
                auto_rename = True
                continue
            try:
                filename = validate_safe_filename(replacement, fmt)
                auto_rename = False
            except ValueError as error:
                print(f"Invalid filename: {error}")
        except (OSError, ValueError) as error:
            print(f"Could not export route: {redact(str(error), key)}")
            return None


def prompt_route_export(record, export_dir=EXPORTS_DIR, key=None, allow_profile_shortcut=False):
    """Ask the user whether to export the route after displaying it."""
    while True:
        answer = input("Would you like to export this route? (yes/no): ").strip().lower()
        if answer in ("q", "quit"):
            return "QUIT"
        if answer in ("no", "n"):
            return None
        if answer in ("yes", "y"):
            return prompt_export_format_and_save(record, export_dir=export_dir, key=key)
        if allow_profile_shortcut and answer in PROFILES:
            return f"PROFILE:{answer}"
        print("Please answer yes or no, or q to quit.")


def display_route_history(history):
    """Print the indexed list of routes stored in the current session."""
    entries = history.entries()
    if not entries:
        print("No routes in session history yet.")
        return False
    print("\nROUTE HISTORY")
    print("=" * 50)
    for index, record in enumerate(entries, start=1):
        print(
            f"{index:>2}. {record.origin} -> {record.destination} | "
            f"Profile: {record.profile} | "
            f"Distance: {record.formatted_distance} | "
            f"Duration: {record.formatted_duration}"
        )
    print("=" * 50)
    return True


def select_history_record(history, action_label="view"):
    """Prompt the user to pick a route from session history or cancel safely."""
    if not display_route_history(history):
        return None
    total = len(history)
    prompt_text = f"Select a route to {action_label} (1-{total}), or C to cancel: "
    while True:
        choice = input(prompt_text).strip()
        if choice.lower() in ("c", "cancel", "b", "back", "q", "quit"):
            return None
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= total:
                return history.get(index)
        print(f"Invalid selection. Please enter a number from 1 to {total}, or C to cancel.")


def handle_view_history(history):
    """View a previously generated route from session history without API calls."""
    record = select_history_record(history, action_label="view")
    if record is None:
        return
    display_route(record, output_mode="detailed")


def handle_export_history(history, export_dir=EXPORTS_DIR, key=None):
    """Export a previously generated route from session history without API calls."""
    record = select_history_record(history, action_label="export")
    if record is None:
        return None
    return prompt_export_format_and_save(record, export_dir=export_dir, key=key)


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


def print_main_menu():
    """Display the main terminal navigation menu."""
    print("\n" + "=" * 40)
    print("             DEVASC ROUTE FINDER")
    print("=" * 40)
    print("\n1. Find a Route")
    print("2. View Route History")
    print("3. Export Previous Route")
    print("4. Exit\n")


def find_route_workflow(key, history, export_dir=EXPORTS_DIR, initial_profile=None):
    """Execute the interactive route-finding workflow.

    Returns 'QUIT' if the user enters q/quit at a prompt, or 'MENU' when the
    workflow completes or recovers to return to the main menu.
    """
    shortcut_mode = initial_profile is not None
    profile = initial_profile
    while True:
        if profile is None:
            profile = read_input("Travel profile (car, bike, foot): ")
            if profile is None:
                return "QUIT"
        profile = profile.lower()
        if profile not in PROFILES:
            profile = "car"
            print("Unknown profile. Using car.")
        units = read_units()
        if units is None:
            return "QUIT"
        output_mode = read_output_mode()
        if output_mode is None:
            return "QUIT"
        location = read_input("Starting location: ")
        if location is None:
            return "QUIT"
        origin = geocoding(location, key)
        if origin[0] is None:
            return "QUIT"
        if origin[1] is None or origin[2] is None:
            return "MENU"
        location = read_input("Destination: ")
        if location is None:
            return "QUIT"
        destination = geocoding(location, key)
        if destination[0] is None:
            return "QUIT"
        if destination[1] is None or destination[2] is None:
            return "MENU"
        path = routing(origin, destination, profile, key)
        if path is None:
            return "MENU"

        display_route(path, origin[3], destination[3], profile, units, output_mode)
        record = create_route_record(path, origin, destination, profile, units, key=key)
        history.add(record)
        export_status = prompt_route_export(
            record,
            export_dir=export_dir,
            key=key,
            allow_profile_shortcut=shortcut_mode,
        )
        if export_status == "QUIT":
            return "QUIT"
        if isinstance(export_status, str) and export_status.startswith("PROFILE:"):
            profile = export_status.split(":", 1)[1]
            continue
        return "MENU"


def main(export_dir=EXPORTS_DIR):
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    key = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    if not key or key == "replace_with_your_own_key":
        print("Set GRAPHHOPPER_API_KEY in the project's .env file or your environment.")
        return 1

    history = RouteHistory(max_size=MAX_HISTORY_SIZE)
    print("DEVASC Option 1 — GraphHopper lab baseline. Enter q or quit to exit.")
    while True:
        try:
            print_main_menu()
            option = input("Select an option: ").strip().lower()
            if option in ("4", "q", "quit", "exit"):
                break
            if option == "1":
                status = find_route_workflow(key, history, export_dir=export_dir)
                if status == "QUIT":
                    break
            elif option in PROFILES:
                status = find_route_workflow(
                    key, history, export_dir=export_dir, initial_profile=option
                )
                if status == "QUIT":
                    break
            elif option == "2":
                handle_view_history(history)
            elif option == "3":
                handle_export_history(history, export_dir=export_dir, key=key)
            else:
                print("Invalid option. Please choose 1, 2, 3, or 4.")
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
