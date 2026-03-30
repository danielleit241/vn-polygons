# Vietnam Provinces GeoJSON with OSM Map

This project converts a Vietnam provinces shapefile into GeoJSON, splits each province/city into a standalone JSON file, and renders an interactive OpenStreetMap (OSM) preview.

## Project Structure

- `main.py`: Reads `Provinces.shp`, normalizes geometry, and exports `Provinces.json`.
- `split_provinces.py`: Splits `Provinces.json` into one file per province in `provinces/`.
- `draw_map.py`: Loads one province JSON file, renders `map_osm.html`, and serves it on `http://127.0.0.1:8000`.
- `Provinces.shp`, `Provinces.shx`: Input shapefile data.

## Requirements

- Python 3.11+ (tested with Python 3.13)
- Windows PowerShell or macOS Terminal (zsh/bash)
- Python packages:
  - geopandas
  - shapely
  - pyogrio
  - folium

## Setup (Windows)

If you already have `.venv`, you can skip environment creation.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install geopandas shapely pyogrio folium
```

## Setup (macOS)

If you already have `.venv`, you can skip environment creation.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install geopandas shapely pyogrio folium
```

## Run Full Pipeline (Windows)

From the project root:

```powershell
python main.py
python split_provinces.py
python draw_map.py can_tho
```

If you do not activate your virtual environment, use:

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe split_provinces.py
.\.venv\Scripts\python.exe draw_map.py can_tho
```

## Run Full Pipeline (macOS)

From the project root:

```bash
python3 main.py
python3 split_provinces.py
python3 draw_map.py can_tho
```

If virtual environment is not activated, use:

```bash
./.venv/bin/python main.py
./.venv/bin/python split_provinces.py
./.venv/bin/python draw_map.py can_tho
```

What you get:

- `Provinces.json` generated from shapefile
- `provinces/*.json` generated (one per province/city)
- `map_osm.html` generated and served locally

Open map in browser:

- `http://127.0.0.1:8000/map_osm.html`

## Draw Another Province

You can pass either a province name or a slug file name:

```bash
python draw_map.py "Cần Thơ"
python draw_map.py can_tho
```

On macOS, replace `python` with `python3` if needed.

If no argument is provided, `draw_map.py` shows all available provinces/cities and asks for input interactively.

## Common Issues

1. SHX index issue (`Unable to open Provinces.shx`)

- `main.py` already sets `SHAPE_RESTORE_SHX=YES` automatically.

2. CRS warning when exporting GeoJSON

- This warning does not break the pipeline.
- If you need CRS metadata, assign CRS in `main.py` before export.

## Notes

- Province display names are stored under the `province_name` property.
- Generated outputs are ignored by Git via `.gitignore`.
