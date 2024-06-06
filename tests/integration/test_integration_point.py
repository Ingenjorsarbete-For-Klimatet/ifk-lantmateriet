"""Point integration tests."""

import geopandas as gpd
from geopandas import testing
from lantmateriet.point import Point

test_byggnad_geojson = gpd.read_file(
    "tests/fixtures/test_integration_construction_byggnad.geojson",
    layer="byggnad",
    use_arrow=True,
)
test_byggnad_geojson.to_file(
    "tests/fixtures/test_integration_construction_byggnad.gpkg",
    layer="byggnad",
    driver="GPKG",
)

test_byggnad_result = gpd.read_file(
    "tests/fixtures/test_integration_construction_byggnad_result.geojson",
    layer="byggnad",
    where="objekttyp='Bostad'",
    engine="pyogrio",
    use_arrow=True,
)
test_byggnad_result.drop(columns=["area_m2", "length_m"], inplace=True)
test_byggnad_result["objekttypnr"] = test_byggnad_result["objekttypnr"].astype("int64")


class TestIntegrationPoint:
    """Integration test of Point."""

    def test_integration_get_buiding_items(self):
        """Integration test of Point process."""
        point = Point(
            "tests/fixtures/test_integration_construction_byggnad.gpkg",
            "50",
            "byggnad",
            "Bostad",
            "objekttyp",
        )
        point.process()

        testing.assert_geodataframe_equal(
            point.df,
            test_byggnad_result,
            check_like=True,
            check_dtype=False,
        )
