import os

import geopandas as gpd
from shapely.geometry import LineString, Polygon

INPUT_SHP_PATH = "Provinces.shp"
OUTPUT_GEOJSON_PATH = "Provinces.json"
PROVINCE_NAME_FIELD = "province_name"
OFFICIAL_PROVINCE_CITY_NAMES = [
	"An Giang",
	"Bắc Ninh",
	"Cà Mau",
	"Cần Thơ",
	"Cao Bằng",
	"Đà Nẵng",
	"Đắk Lắk",
	"Điện Biên",
	"Đồng Nai",
	"Đồng Tháp",
	"Gia Lai",
	"Hà Tĩnh",
	"Hà Nội",
	"Hải Phòng",
	"Huế",
	"Hưng Yên",
	"Khánh Hòa",
	"Lai Châu",
	"Lâm Đồng",
	"Lạng Sơn",
	"Lào Cai",
	"Nghệ An",
	"Ninh Bình",
	"Phú Thọ",
	"Quảng Ngãi",
	"Quảng Ninh",
	"Quảng Trị",
	"Sơn La",
	"Tây Ninh",
	"Thái Nguyên",
	"Thanh Hóa",
	"Tuyên Quang",
	"Vĩnh Long",
	"TP. Hồ Chí Minh",
]


def _to_polygon_if_linestring(geometry):
	if isinstance(geometry, LineString):
		return Polygon(geometry.coords)
	return geometry


def main() -> None:
	# Recover missing/corrupted .shx index automatically when reading shapefile.
	os.environ.setdefault("SHAPE_RESTORE_SHX", "YES")

	province_gdf = gpd.read_file(INPUT_SHP_PATH)
	province_gdf["geometry"] = province_gdf["geometry"].apply(_to_polygon_if_linestring)

	if len(province_gdf) != len(OFFICIAL_PROVINCE_CITY_NAMES):
		raise ValueError(
			"Feature count does not match official name list: "
			f"{len(province_gdf)} != {len(OFFICIAL_PROVINCE_CITY_NAMES)}"
		)

	province_gdf[PROVINCE_NAME_FIELD] = OFFICIAL_PROVINCE_CITY_NAMES
	province_gdf.to_file(OUTPUT_GEOJSON_PATH, driver="GeoJSON")

	print(f"Exported {len(province_gdf)} features to {OUTPUT_GEOJSON_PATH}")


if __name__ == "__main__":
	main()