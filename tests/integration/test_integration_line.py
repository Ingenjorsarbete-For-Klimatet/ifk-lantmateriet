"""Line integration tests."""

import geopandas as gpd
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
    where="objekttyp='Motorväg'",
    engine="pyogrio",
    use_arrow=True,
)
test_vaglinje_result["objekttypnr"] = test_vaglinje_result["objekttypnr"].astype("int64")


class TestIntegrationLine:
    """Integration test of Line."""

    def test_integration_get_buiding_items(self):
        """Integration test of Line process."""
        line = Line(
            "tests/fixtures/test_integration_communication_vaglinje.gpkg",
            "50",
            "vaglinje",
            "Motorväg",
            "objekttyp",
        )
        line.process()

        testing.assert_geodataframe_equal(
            line.df,
            test_vaglinje_result,
            check_like=True,
            check_dtype=False,
        )
