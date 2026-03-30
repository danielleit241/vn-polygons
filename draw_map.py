import json
import re
import socket
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Iterator

import folium

PROVINCE_NAME_FIELD = "province_name"
PROVINCES_DIRECTORY = Path("provinces")
OUTPUT_MAP_PATH = Path("map_osm.html")
PREVIEW_PORT = 8000


def _iter_lon_lat(geometry: dict) -> Iterator[tuple[float, float]]:
    """Duyet qua toa do (lon, lat) tu hinh hoc Polygon/MultiPolygon."""
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        for ring in coords:
            for lon, lat in ring:
                yield lon, lat
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                for lon, lat in ring:
                    yield lon, lat


def _slugify(text: str) -> str:
    normalized_text = text.replace("Đ", "D").replace("đ", "d")
    normalized_text = unicodedata.normalize("NFKD", normalized_text)
    ascii_text = normalized_text.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    return ascii_text.strip("_")


def _compute_center(features: list[dict]) -> tuple[float, float]:
    longitudes: list[float] = []
    latitudes: list[float] = []

    for feature in features:
        geometry = feature.get("geometry") or {}
        for lon, lat in _iter_lon_lat(geometry):
            longitudes.append(lon)
            latitudes.append(lat)

    if not longitudes or not latitudes:
        return 16.0, 106.0

    return (min(latitudes) + max(latitudes)) / 2, (min(longitudes) + max(longitudes)) / 2


def _load_available_province_names(province_dir: Path) -> list[str]:
    province_names: list[str] = []

    for province_file in sorted(province_dir.glob("*.json")):
        try:
            with province_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            features = data.get("features", [])
            first_feature = features[0] if features else {}
            properties = first_feature.get("properties") or {}
            display_name = properties.get(PROVINCE_NAME_FIELD) or province_file.stem
        except Exception:
            display_name = province_file.stem
        province_names.append(display_name)

    return province_names


def _resolve_input_name(province_dir: Path) -> str:
    if len(sys.argv) > 1:
        return sys.argv[1].strip()

    available_names = _load_available_province_names(province_dir)
    if available_names:
        print("Available provinces/cities:")
        for index, province_name in enumerate(available_names, start=1):
            print(f"{index}. {province_name}")
        print()

    user_input = input("Enter province/city name or file name (e.g. Can Tho / can_tho): ").strip()
    if not user_input:
        raise ValueError("No input was provided.")
    return user_input


def _resolve_province_file(input_name: str, province_dir: Path) -> Path:
    slug = _slugify(input_name)
    if not slug:
        raise ValueError("Invalid input value.")

    direct_path = province_dir / f"{slug}.json"
    if direct_path.exists():
        return direct_path

    available_names = ", ".join(path.stem for path in sorted(province_dir.glob("*.json")))
    raise FileNotFoundError(
        f"Could not find a file for '{input_name}'. Looked for '{slug}.json' in '{province_dir}'. "
        f"Available files: {available_names}"
    )


def _is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _start_local_http_server(port: int, serving_directory: Path) -> bool:
    if _is_port_in_use(port):
        return False

    subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(serving_directory),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return True


def main() -> None:
    input_name = _resolve_input_name(PROVINCES_DIRECTORY)
    province_file_path = _resolve_province_file(input_name, PROVINCES_DIRECTORY)

    with province_file_path.open("r", encoding="utf-8") as file:
        province_geojson = json.load(file)

    province_features = province_geojson.get("features", [])
    if not province_features:
        raise ValueError(f"File {province_file_path} does not contain any features.")

    center_latitude, center_longitude = _compute_center(province_features)
    province_name = (province_features[0].get("properties") or {}).get(PROVINCE_NAME_FIELD, province_file_path.stem)

    map_view = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=10,
        tiles="OpenStreetMap",
    )

    folium.GeoJson(
        province_geojson,
        name=province_name,
        style_function=lambda _: {
            "color": "#1f4e79",
            "weight": 1,
            "fillColor": "#2a9d8f",
            "fillOpacity": 0.25,
        },
        tooltip=folium.GeoJsonTooltip(fields=[PROVINCE_NAME_FIELD], aliases=["Tỉnh/Thành:"]),
    ).add_to(map_view)

    folium.LayerControl().add_to(map_view)
    map_view.save(OUTPUT_MAP_PATH)

    print(f"Map generated for {province_name}: {OUTPUT_MAP_PATH}")
    print(f"Data source: {province_file_path}")

    started_new_server = _start_local_http_server(PREVIEW_PORT, Path.cwd())
    preview_url = f"http://127.0.0.1:{PREVIEW_PORT}/{OUTPUT_MAP_PATH.name}"

    if started_new_server:
        print(f"Started HTTP server on port {PREVIEW_PORT}")
    else:
        print(f"HTTP server is already running on port {PREVIEW_PORT}")

    print(f"Open the map at: {preview_url}")


if __name__ == "__main__":
    main()
