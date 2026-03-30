import json
import re
import unicodedata
from pathlib import Path

SOURCE_GEOJSON_PATH = Path("Provinces.json")
OUTPUT_DIRECTORY = Path("provinces")
PROVINCE_NAME_FIELD = "province_name"


def slugify(text: str) -> str:
    text = text.replace("Đ", "D").replace("đ", "d")
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    return ascii_text.strip("_") or "unknown"


def _load_features(source_path: Path) -> list[dict]:
    with source_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    features = data.get("features", [])
    if not features:
        raise ValueError(f"File {source_path} does not contain any features.")
    return features


def _clear_old_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for json_file in output_dir.glob("*.json"):
        json_file.unlink()


def _build_output_feature(feature: dict) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [feature],
    }


def main() -> None:
    features = _load_features(SOURCE_GEOJSON_PATH)
    _clear_old_outputs(OUTPUT_DIRECTORY)

    used_names: dict[str, int] = {}

    for feature in features:
        props = feature.get("properties") or {}
        province_name = props.get(PROVINCE_NAME_FIELD) or "Unknown"

        base_name = slugify(province_name)
        suffix = used_names.get(base_name, 0)
        used_names[base_name] = suffix + 1
        file_stem = base_name if suffix == 0 else f"{base_name}_{suffix + 1}"

        single_feature = _build_output_feature(feature)

        out_path = OUTPUT_DIRECTORY / f"{file_stem}.json"
        with out_path.open("w", encoding="utf-8") as out_file:
            json.dump(single_feature, out_file, ensure_ascii=False, indent=2)

    print(f"Split {len(features)} features into {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
