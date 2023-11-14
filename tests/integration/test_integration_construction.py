"""Construction integration tests."""
import geopandas as gpd
import pandas as pd
from geopandas import testing
from lantmateriet.construction import Construction

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
    use_arrow=True,
)


class TestIntegrationConstruction:
    """Integration test of Construction."""

    def test_integration_get_buiding_items(self):
        """Integration test of Construction process."""
        construction = Construction(
            "tests/fixtures/test_integration_construction_byggnad.gpkg",
            "50",
            "byggnad",
            True,
        )
        df = construction.process()
        df = pd.concat([v for _, v in df.items()], ignore_index=True)

        testing.assert_geodataframe_equal(df, test_byggnad_result, check_like=True)
