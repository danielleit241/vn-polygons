import json

import pytest

from app.models.administrative_unit import AdministrativeUnit
from app.models.province import Province
from app.schemas.administrative_region import AdministrativeRegionCreate, AdministrativeRegionUpdate
from app.schemas.administrative_unit import AdministrativeUnitCreate, AdministrativeUnitUpdate
from app.schemas.province import ProvinceCreate, ProvinceUpdate
from app.schemas.ward import WardCreate, WardUpdate
from app.services import (
    administrative_regions_service,
    administrative_units_service,
    provinces_service,
    wards_service,
)


def test_administrative_regions_service_crud(db_session):
    created = administrative_regions_service.create_region(
        db_session,
        AdministrativeRegionCreate(
            id=1,
            name="Dong Bac Bo",
            name_en="Northeast",
            code_name="dong_bac_bo",
            code_name_en="northeast",
        ),
    )
    assert created.id == 1

    listed = administrative_regions_service.list_regions(db_session)
    assert len(listed) == 1

    fetched = administrative_regions_service.get_region(db_session, 1)
    assert fetched.name_en == "Northeast"

    updated = administrative_regions_service.update_region(
        db_session,
        1,
        AdministrativeRegionUpdate(name="Tay Bac Bo", name_en="Northwest"),
    )
    assert updated.name == "Tay Bac Bo"

    administrative_regions_service.delete_region(db_session, 1)
    assert administrative_regions_service.list_regions(db_session) == []


def test_administrative_regions_service_errors(db_session):
    with pytest.raises(LookupError):
        administrative_regions_service.get_region(db_session, 999)

    administrative_regions_service.create_region(
        db_session,
        AdministrativeRegionCreate(
            id=2,
            name="A",
            name_en="A",
            code_name="a",
            code_name_en="a",
        ),
    )

    with pytest.raises(ValueError):
        administrative_regions_service.create_region(
            db_session,
            AdministrativeRegionCreate(
                id=2,
                name="B",
                name_en="B",
                code_name="b",
                code_name_en="b",
            ),
        )


def test_administrative_units_service_crud(db_session):
    created = administrative_units_service.create_unit(
        db_session,
        AdministrativeUnitCreate(
            id=1,
            full_name="Tinh",
            full_name_en="Province",
            short_name="Tinh",
            short_name_en="Province",
            code_name="tinh",
            code_name_en="province",
        ),
    )
    assert created.id == 1

    fetched = administrative_units_service.get_unit(db_session, 1)
    assert fetched.code_name == "tinh"

    updated = administrative_units_service.update_unit(
        db_session,
        1,
        AdministrativeUnitUpdate(full_name="Thanh pho", full_name_en="City"),
    )
    assert updated.full_name == "Thanh pho"

    administrative_units_service.delete_unit(db_session, 1)
    assert administrative_units_service.list_units(db_session) == []


def test_administrative_units_service_errors(db_session):
    with pytest.raises(LookupError):
        administrative_units_service.get_unit(db_session, 999)

    administrative_units_service.create_unit(
        db_session,
        AdministrativeUnitCreate(
            id=3,
            full_name="Tinh",
            full_name_en="Province",
            short_name="Tinh",
            short_name_en="Province",
            code_name="tinh",
            code_name_en="province",
        ),
    )

    with pytest.raises(ValueError):
        administrative_units_service.create_unit(
            db_session,
            AdministrativeUnitCreate(
                id=3,
                full_name="Dup",
                full_name_en="Dup",
                short_name="Dup",
                short_name_en="Dup",
                code_name="dup",
                code_name_en="dup",
            ),
        )


def _seed_unit_for_foreign_key_tests(db_session, unit_id: int = 10):
    db_session.add(
        AdministrativeUnit(
            id=unit_id,
            full_name="Tinh",
            full_name_en="Province",
            short_name="Tinh",
            short_name_en="Province",
            code_name="tinh",
            code_name_en="province",
        )
    )
    db_session.commit()


def test_provinces_service_crud(db_session):
    _seed_unit_for_foreign_key_tests(db_session, 10)

    created = provinces_service.create_province(
        db_session,
        ProvinceCreate(
            code="01",
            name="Ha Noi",
            name_en="Ha Noi",
            full_name="Thanh pho Ha Noi",
            full_name_en="Ha Noi City",
            code_name="ha_noi",
            boundary_geojson={"type": "Polygon", "coordinates": []},
            administrative_unit_id=10,
        ),
    )
    assert created.code == "01"

    fetched = provinces_service.get_province(db_session, "01")
    assert fetched.name == "Ha Noi"

    updated = provinces_service.update_province(
        db_session,
        "01",
        ProvinceUpdate(name="Ha Noi Moi", full_name="Thanh pho Ha Noi Moi"),
    )
    assert updated.name == "Ha Noi Moi"

    provinces_service.delete_province(db_session, "01")
    assert provinces_service.list_provinces(db_session) == []


def test_provinces_service_errors(db_session):
    with pytest.raises(LookupError):
        provinces_service.get_province(db_session, "missing")

    with pytest.raises(ValueError):
        provinces_service.create_province(
            db_session,
            ProvinceCreate(
                code="99",
                name="Test",
                name_en="Test",
                full_name="Tinh Test",
                full_name_en="Test",
                code_name="test",
                boundary_geojson=None,
                administrative_unit_id=999,
            ),
        )


def test_province_polygons_import_service(db_session, tmp_path):
    _seed_unit_for_foreign_key_tests(db_session, 11)

    db_session.add(
        Province(
            code="11",
            name="Test Province",
            name_en="Test Province",
            full_name="Tinh Test",
            full_name_en="Test Province",
            code_name="test_province",
            boundary_geojson=None,
            administrative_unit_id=11,
        )
    )
    db_session.add(
        Province(
            code="12",
            name="Missing Province",
            name_en="Missing Province",
            full_name="Tinh Missing",
            full_name_en="Missing Province",
            code_name="missing_province",
            boundary_geojson=None,
            administrative_unit_id=11,
        )
    )
    db_session.commit()

    polygon_file = tmp_path / "test_province.json"
    polygon_file.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}}],
            }
        ),
        encoding="utf-8",
    )

    result = provinces_service.import_province_polygons(db_session, str(tmp_path))
    assert result.updated == 1
    assert "12" in result.missing_files


def test_wards_service_crud(db_session):
    _seed_unit_for_foreign_key_tests(db_session, 20)
    db_session.add(
        Province(
            code="79",
            name="Ho Chi Minh",
            name_en="Ho Chi Minh",
            full_name="Thanh pho Ho Chi Minh",
            full_name_en="Ho Chi Minh City",
            code_name="ho_chi_minh",
            boundary_geojson=None,
            administrative_unit_id=20,
        )
    )
    db_session.commit()

    created = wards_service.create_ward(
        db_session,
        WardCreate(
            code="00001",
            name="Ward 1",
            name_en="Ward 1",
            full_name="Phuong 1",
            full_name_en="Ward 1",
            code_name="ward_1",
            province_code="79",
            administrative_unit_id=20,
        ),
    )
    assert created.code == "00001"

    listed = wards_service.list_wards(db_session, province_code="79")
    assert len(listed) == 1

    fetched = wards_service.get_ward(db_session, "00001")
    assert fetched.name == "Ward 1"

    updated = wards_service.update_ward(db_session, "00001", WardUpdate(name="Ward 1 Updated"))
    assert updated.name == "Ward 1 Updated"

    wards_service.delete_ward(db_session, "00001")
    assert wards_service.list_wards(db_session) == []


def test_wards_service_errors(db_session):
    with pytest.raises(LookupError):
        wards_service.get_ward(db_session, "missing")

    with pytest.raises(ValueError):
        wards_service.create_ward(
            db_session,
            WardCreate(
                code="00002",
                name="Ward 2",
                name_en="Ward 2",
                full_name="Phuong 2",
                full_name_en="Ward 2",
                code_name="ward_2",
                province_code="01",
                administrative_unit_id=1,
            ),
        )
