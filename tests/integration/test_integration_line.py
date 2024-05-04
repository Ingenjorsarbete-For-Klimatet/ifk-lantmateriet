"""Line integration tests."""

import geopandas as gpd
import pandas as pd
from geopandas import testing
from lantmateriet.line import Line

test_vaglinje_geojson = gpd.read_file(
    "tests/fixtures/test_integration_communication_vaglinje.geojson",
    layer="vaglinje",
    use_arrow=True,
)
test_vaglinje_geojson.to_file(
    "tests/fixtures/test_integration_communication_vaglinje.gpkg",
    layer="vaglinje",
    driver="GPKG",
)

test_vaglinje_result = gpd.read_file(
    "tests/fixtures/test_integration_communication_vaglinje_result.geojson",
    layer="vaglinje",
    use_arrow=True,
)


class TestIntegrationLine:
    """Integration test of Line."""

    def test_integration_get_buiding_items(self):
        """Integration test of Line process."""
        communication = Line(
            "tests/fixtures/test_integration_communication_vaglinje.gpkg",
            "50",
            "vaglinje",
            True,
        )
        df = communication.process()
        df = pd.concat([v for _, v in df.items()], ignore_index=True)

        testing.assert_geodataframe_equal(df, test_vaglinje_result, check_like=True)
