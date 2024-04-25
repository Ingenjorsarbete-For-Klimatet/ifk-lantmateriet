"""Ground integration tests."""

import geopandas as gpd
import pandas as pd
from geopandas import testing
from lantmateriet.polygon import Ground

test_mark_geojson = gpd.read_file(
    "tests/fixtures/test_integration_ground_mark.geojson", layer="mark", use_arrow=True
)
test_mark_geojson.to_file(
    "tests/fixtures/test_integration_ground_mark.gpkg", layer="mark", driver="GPKG"
)

test_mark_result = gpd.read_file(
    "tests/fixtures/test_integration_ground_mark_result.geojson",
    layer="mark",
    use_arrow=True,
)


class TestIntegrationGround:
    """Integration test of Ground."""

    def test_integration_get_ground_items(self):
        """Integration test of Ground processd."""
        ground = Ground(
            "tests/fixtures/test_integration_ground_mark.gpkg", "50", "mark", True
        )
        df = ground.process()
        df = pd.concat([v for _, v in df.items()], ignore_index=True)

        testing.assert_geodataframe_equal(df, test_mark_result, check_like=True)
