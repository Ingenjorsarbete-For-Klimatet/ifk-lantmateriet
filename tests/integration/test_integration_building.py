"""Building integration tests."""
import geopandas as gpd
import pandas as pd
from geopandas import testing
from lantmateriet.building import Building

test_byggnad_geojson = gpd.read_file(
    "tests/fixtures/test_integration_building_byggnad.geojson",
    layer="byggnad",
    use_arrow=True,
)
test_byggnad_geojson.to_file(
    "tests/fixtures/test_integration_building_byggnad.gpkg",
    layer="byggnad",
    driver="GPKG",
)

test_byggnad_result = gpd.read_file(
    "tests/fixtures/test_integration_building_byggnad_result.geojson",
    layer="byggnad",
    use_arrow=True,
)


class TestIntegrationBuilding:
    """Integration test of Building."""

    def test_integration_get_buiding_items(self):
        """Integration test of Building process."""
        building = Building(
            "tests/fixtures/test_integration_building_byggnad.gpkg",
            "50",
            "byggnad",
            True,
        )
        df = building.process()
        df = pd.concat([v for _, v in df.items()], ignore_index=True)

        testing.assert_geodataframe_equal(df, test_byggnad_result, check_like=True)
